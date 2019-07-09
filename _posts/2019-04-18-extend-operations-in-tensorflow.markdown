---
layout: post
title:  "Create an op in tensorflow (Partial)"
date:   2019-04-18
categories: tensorflow
author: moontree
---

官网给出了添加新操作的[文档](https://www.tensorflow.org/guide/extend/op)，用作示例是比较详细了，但是有些细节还是不够清楚。

## 何时需要添加新操作？
- 无法轻易或根本无法将您的操作表示为现有操作的组合
- 将操作表示为现有基本功能的组合并不高效
- 想以手动方式混合未来的编译器难以混合的基本功能

## 添加自定义操作的步骤
- 在 C++ 文件中注册新操作。

    操作注册定义了操作功能的接口（规范），此接口与操作的实现无关。
    例如，操作注册定义了操作的名称及操作的输入和输出，
    还定义了用于张量形状推断的形状函数。
- 用 C++ 实现操作。

    操作的实现称为内核，
    它是您在第 1 步中注册的规范的具体实现。
    可以有多个内核用于不同的输入/输出类型或架构（例如，CPU、GPU）。
- 创建一个 Python 封装容器（可选)。

    这个封装容器是用于以 Python 创建操作的公共 API。
    默认封装容器是根据操作注册生成的，您可以直接使用它或向其添加内容。

- 编写一个函数来计算操作的梯度（可选）。
- 测试操作。

## 示例及解析

### 注册操作接口
``` c++
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"

using namespace tensorflow;

REGISTER_OP("ZeroOut")
    .Input("to_zero: int32")
    .Output("zeroed: int32")
    .SetShapeFn([](::tensorflow::shape_inference::InferenceContext* c) {
      c->set_output(0, c->input(0));
      return Status::OK();
    });
```

这段代码看起来还比较好理解，指定输入、输出的Tensor名称及类型，自动推理输出形状。

可是InferenceContext具体是怎样的呢？下面从[`tensorflow/tensorflow/core/framework/shape_inference.h`](https://github.com/tensorflow/tensorflow/blob/9fd7cf0547e2f93502c50088879ba30e4e53ad2c/tensorflow/core/framework/shape_inference.h)
中节选了部分有用的代码

```
class InferenceContext {
    private:
        // inputs_, outputs_, and input_tensors_as_shapes_ refer to values from
        // `shape_manager_`.
        std::vector<ShapeHandle> inputs_;
        std::vector<const Tensor*> input_tensors_;
        std::vector<bool> requested_input_tensor_;
        std::vector<ShapeHandle> outputs_;
        // Can have fewer elements than inputs_.
        std::vector<ShapeHandle> input_tensors_as_shapes_;
        std::vector<bool> requested_input_tensor_as_partial_shape_;
    public:

        InferenceContext(int graph_def_version, const NodeDef* node_def, const OpDef& op_def, const std::vector<ShapeHandle>& input_shapes,
            const std::vector<const Tensor*>& input_tensors, const std::vector<ShapeHandle>& input_tensors_as_shapes,
            std::vector<std::unique_ptr<std::vector<ShapeAndType>>>
            input_handle_shapes_and_types
        );
        ~InferenceContext();
        Status Run(const std::function<Status(shape_inference::InferenceContext* c)>& fn);
        ShapeHandle input(int64 idx) const { return inputs_[idx]; }
        void set_output(int idx, ShapeHandle shape) { outputs_[idx] = shape; }
}
```
