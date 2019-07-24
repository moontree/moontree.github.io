---
layout: post
title:  "tf.slim.batch_norm使用注意事项"
date:   2019-07-23
categories: tensorflow
author: moontree
---

#
最近在使用tensorflow的slim模块时，又踩了一个坑。其实这个坑之前踩过一部分，但是忘记了。为了后续便于查阅，还是记一下吧。

这次是在使用slim的inception v3时，训练结果很好，但是测试的时候结果就很差。

意识到可能是batchnorm的问题，但是首先想到的是没有利用moving_mean和moving variance，然而查看权重文件时，
这些变量都是存在的---万万不该，没有查看它们的值！

后来搜索后发现，是因为在训练时没有更新，而是保持了初始值！

解决方案有两种：
- 更新train op时同步更新batchnorm的op，如下所示
```
update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
if update_ops:
    with ops.control_dependencies(update_ops):
        barrier = control_flow_ops.no_op(name='update_barrier')
    total_loss = control_flow_ops.with_dependencies([barrier], total_loss)
```
- 或者直接使用slim来创建train op
```
update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
train_op = slim.learning.create_train_op(
    cross_entropy,
    optimizer,
    global_step=step,
    update_op=update_ops
)
```

查看代码后可以发现，前者的代码出现在后者中，本质是一样的，都是先更新batchnorm的值，然后去计算loss等。

突然想到了当时手写多卡训练梯度平均的时候，貌似也是batchnorm没有更新，然而忘记记下来了……


据说还可能有第二个坑，"训练结果很好，但是测试的结果要差上不少"，如果训练步数过少，但是` batch_norm_decay`这个值过大的话，
可能会导致mean 和 variance和初始值变化不大。


