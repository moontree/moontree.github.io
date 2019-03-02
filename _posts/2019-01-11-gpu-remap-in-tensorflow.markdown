---
layout: post
title:  "GPU remap in tensorflow"
date:   2019-01-12
categories: tensorflow
author: moontree
---

训练tensorflow模型的时候，可以通过`tf.device('/gpu:0')`这种方式来为图节点分配不同的gpu。
那么，在推理阶段，该如何将不同的模型分配到不同的gpu上去执行呢？
比如这种场景，有4个模型，每个模型占据6G显存，这样的话，它们必须被分配到不同的GPU上才不会导致显存溢出。

然而，在搜索"tensorflow分配gpu"的时候，通常会出现3种结果：
- 训练时指定，也就是上述方式
- 命令行指定，`CUDA_VISIBLE_DEVICES=0,1 python *.py`，然而，这种方式只能防止tensorflow使用其他的gpu，并不能将4个模型指定到不同的设备上
- 代码中指定，`os.environ['CUDA_VISIBLE_DEVCIES']=0`，然而，这种方式也有问题，不管指定多少次，最终只会使用一个gpu，具体哪个和实际分配的顺序有关

看起来，上述三种方式中，后面两种都不能满足我的需求。
第一种应该是可行的，但是似乎有些不够优雅。有没有更优雅的方式呢？

考虑到之前，为了限制gpu的内存使用，
我们会在创建Session的时候加以限制：
```python
gpu_options=tf.GPUOptions(allow_growth=True)
tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=gpu_options))
```
看来在`tf.GPUOptions`里面，可以对gpu做限制，很好，来看一下[官方文档](https://www.tensorflow.org/api_docs/python/tf/GPUOptions)，
很简单的描述，看来要去[代码](https://github.com/tensorflow/tensorflow/blob/r1.12/tensorflow/core/protobuf/config.proto)里查看了。
搜索关键字`device`，发现了如下描述：
```
  // A comma-separated list of GPU ids that determines the 'visible'
  // to 'virtual' mapping of GPU devices.  For example, if TensorFlow
  // can see 8 GPU devices in the process, and one wanted to map
  // visible GPU devices 5 and 3 as "/device:GPU:0", and "/device:GPU:1",
  // then one would specify this field as "5,3".  This field is similar in
  // spirit to the CUDA_VISIBLE_DEVICES environment variable, except
  // it applies to the visible GPU devices in the process.
  //
  // NOTE:
  // 1. The GPU driver provides the process with the visible GPUs
  //    in an order which is not guaranteed to have any correlation to
  //    the *physical* GPU id in the machine.  This field is used for
  //    remapping "visible" to "virtual", which means this operates only
  //    after the process starts.  Users are required to use vendor
  //    specific mechanisms (e.g., CUDA_VISIBLE_DEVICES) to control the
  //    physical to visible device mapping prior to invoking TensorFlow.
  // 2. In the code, the ids in this list are also called "platform GPU id"s,
  //    and the 'virtual' ids of GPU devices (i.e. the ids in the device
  //    name "/device:GPU:<id>") are also called "TF GPU id"s. Please
  //    refer to third_party/tensorflow/core/common_runtime/gpu/gpu_id.h
  //    for more information.
  string visible_device_list = 5;
```
看起来不错，似乎只要在gpuoptions里加上一个参数就可以了。
代码调整如下：

```python
gpu_options_1=tf.GPUOptions(allow_growth=True, visible_device_list='1')
session1 = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=gpu_options_1))
gpu_options_2=tf.GPUOptions(allow_growth=True, visible_device_list='2')
session2 = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=gpu_options_2))
```

看起来很完美！
然而，错误总在你猝不及防的时候出现——
```python
tensorflow.python.framework.errors_impl.InvalidArgumentError:
'visible_device_list' listed an invalid GPU id '2' but visible device count is 1
```
看起来很奇怪啊，用法没有问题，为什么就报错了呢……

带着求(bao)知(zha)的心态，去搜索这个错误，居然只有两个帖子……
还只有[一个](https://github.com/tensorflow/tensorflow/issues/18861)有效……
不过还好，毕竟有人遇到过同样的问题，那就是个好消息~
然后看到了一个不幸的回复：`gpuoptions`是对整个进程生效的。原文如下：
> Sorry for the confusion, let me clarify:

> it's totally fine to use different configs in different process,
  there is no restriction on that.
  For example, you may set CUDA_VISIBLE_DEVICES=1 in one process and 2 in another,
  you may also set visible_gpu_device or any other ConfigProto options differently.
  in the same process, if possible,
  we should use same GPUOptions for all sessions,
  as most of the options inside GPUOptions are process-wide (AFAIK,
  per_process_gpu_memory_fraction, allocator_type, allow_growth, visible_device_list, experimental are all process-wide options).
  If we use different GPUOptions for different sessions, unexpected behavior may/would occur, depending on which options you set differently.
  In your case, specifically for the code:

>       G =tf.Graph()
>       sess1 = tf.Session(graph=G, config=tf.ConfigProto(log_device_placement=False,gpu_options=tf.GPUOptions(allow_growth=True,visible_device_list='0')))
>       sess2 = tf.Session(graph=G, config=tf.ConfigProto(log_device_placement=False,gpu_options=tf.GPUOptions(allow_growth=True,visible_device_list='1')))

> `sess1` and `sess2` are in same process and using same graph but different GPUOptions options (visible_device_list is different).
> - For `sess1`, a `BaseGPUDevice` will be created with name '/gpu:0' and pointing to physical gpu 0
> - For `sess2`, a `BaseGPUDevice` will be created with name '/gpu:0' but pointing to physical gpu 1.

> Note that both device have same name '/gpu:0',
  so any code that use only the device name (not the BaseGPUDevice object itself)
  to access the physical gpu will be directed to physical gpu 0,
  this is what I called 'unexpected behavior'.
  For example, assume that G has a node placed in '/gpu:0',
  grappler will use the information from physical gpu 0 to optimize your graph in sess2 which is not what we want.

> In order to apply the same graph to different gpu,
 we can use with tf.device() with different device name
 when building/importing the graph.

> Thanks.

哈哈，本宝宝很开心……这居然是一个单进程的设置，会影响session的创建。看了看后续的解释，还是很有道理的。
为了避免冲突，同一进程中的session要用相同的设置，
但是可以把不同的graph放到不同的gpu上执行。
后面给出了一个示例：
```python
from google.protobuf import text_format
import tensorflow as tf

hello = tf.constant('Hello, TensorFlow!')
tf.train.write_graph(tf.get_default_graph(), '/tmp', 'g1')

with open('/tmp/g1', 'rb') as f:
  graph_text = f.read()
print(graph_text)
print('-' * 100)

graphs = []
for g in range(2):
  graphs.append(tf.Graph())
  with graphs[g].as_default():
    graph_def = tf.GraphDef()
    text_format.Merge(graph_text, graph_def)
    with tf.device('/gpu:' + str(g)):
      tf.import_graph_def(graph_def, name='')
    print(tf.get_default_graph().as_graph_def())
    print('-' * 100)

```
貌似可行，但总感觉不够优雅。注意到上述关键字，把不同的图放到不同的gpu上执行，那么，是不是`tf.Graph`本身就支持这样的操作呢？
之前并没有去了解过这个东西：

## tf.Graph and tf.Session

### tf.Graph
tensorflow的计算被表示为数据流图。
一个`Graph`包含了一系列的操作（计算单元，`tf.Operator`)，以及张量（数据单元，`tf.Tensor`）

通常会有一个默认的图，可以通过`tf.get_default_graph`来查看。

可以通过`tf.graph.device('/device:GPU:0')`来指定设备：
```python
with g.device('/device:GPU:0'):
  # All operations constructed in this context will be placed
  # on GPU 0.
  with g.device(None):
    # All operations constructed in this context will have no
    # assigned device.
    pass
```

### tf.Session
> A class for running TensorFlow operations.

> A Session object encapsulates the environment in which Operation objects are executed, and Tensor objects are evaluated. For example:

Session可以捕获操作的环境，并且去运行得到tensor的值。

仔细看下初始化函数，
```python
__init__(
    target='',
    graph=None,
    config=None
)
"""
target: (Optional.) The execution engine to connect to. Defaults to using an in-process engine. See Distributed TensorFlow for more examples.
graph: (Optional.) The Graph to be launched (described above).
config: (Optional.) A ConfigProto protocol buffer with configuration options for the session.
"""
```
很明确了，如果在graph中指定了设备，在session初始化时指定为这个graph，就可以实现之前的目的了。

重点：
graph指定了运行时的设备、操作、张量；而session只是按照graph的指定去运行，本身没有指定设备的功能。


最终示例代码如下：

```python
import tensorflow as tf
import numpy as np
v = np.ones([100 , 1000, 1000])
g1 = tf.Graph()
g2 = tf.Graph()
c = tf.ConfigProto()
c.allow_soft_placement=True
c.gpu_options.allow_growth=True
with g1.as_default(), g1.device('/device:GPU:0'):
    a = tf.constant(v)
with g2.as_default(), g2.device('/device:GPU:1'):
    b = tf.constant(v)
sess1 = tf.Session(graph=g1, config=c)
sess2 = tf.Session(graph=g2, config=c)
```



