# Transfomer

## 0. 问题背景

这里特指序列到序列的模型，基于Attention is all you need这篇论文。我想了解的是如何去工程化的设计模型。

## 1. 序列到序列的步骤

1. 文本序列分词
2. 分词序列编码
3. 整数编码序列词嵌入
4. **transformer模型**
5. 原始对数输出
6. 对数概率化
7. 整数编码序列
8. 解码为文本序列

> 有的模型类会将第3步词嵌入和第5-6步也放到模型实现中去。

## 2. `nn.Transfomer`的设计

如下所示，`torch 2.7.0`对于[`nn.Transfomer`](https://github.com/pytorch/pytorch/blob/v2.7.0/torch/nn/modules/transformer.py#L57)的设计是没有上面的第3、5和6步的。换句话说，`nn.Transfomer`只包含编码器和解码器。

![img](https://pic1.zhimg.com/80/v2-4d0a824d1015a388ed6fd92a3be26f7d_720w.webp?source=1def8aca)

### 2.1 [`nn.Transfomer`的参数](https://pytorch.ac.cn/docs/stable/generated/torch.nn.Transformer.html)

#### 2.1.1 实例化参数

实例化参数用于修改模型的架构或属性。

- **d_model** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 编码器/解码器输入中预期的特征数量（默认值=512，即词嵌入维度）。
- **nhead** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 多头注意力模型中的头数量（默认值=8）。
- **num_encoder_layers** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 编码器中的子编码器层数量（默认值=6）。
- **num_decoder_layers** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 解码器中的子解码器层数量（默认值=6）。
- **dim_feedforward** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 前馈网络模型的维度（默认值=2048，即mlp的中间维度）。

```python
        (linear1): Linear(in_features=512, out_features=2048, bias=True)
        (dropout): Dropout(p=0.1, inplace=False)
        (linear2): Linear(in_features=2048, out_features=512, bias=True)
```

- **dropout** ([*float*](https://docs.pythonlang.cn/3/library/functions.html#float)) – dropout 值（默认值=0.1）。
- **activation** ([*Union*](https://docs.pythonlang.cn/3/library/typing.html#typing.Union)*[*[*str*](https://docs.pythonlang.cn/3/library/stdtypes.html#str)*,* [*Callable*](https://docs.pythonlang.cn/3/library/typing.html#typing.Callable)*[**[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]**,* [*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]**]*) – 编码器/解码器中间层的激活函数，可以是字符串（“relu”或“gelu”）或一元可调用对象。默认值：relu
- **custom_encoder** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Any*](https://docs.pythonlang.cn/3/library/typing.html#typing.Any)*]*) – 自定义编码器（默认值=None）。
- **custom_decoder** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Any*](https://docs.pythonlang.cn/3/library/typing.html#typing.Any)*]*) – 自定义解码器（默认值=None）。
- **layer_norm_eps** ([*float*](https://docs.pythonlang.cn/3/library/functions.html#float)) – 层归一化组件中的 eps 值（默认值=1e-5,即 $\varepsilon$ ：[**防止分母为零的非常小常数**](./layernorm.md)）。
- **batch_first** ([*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)) – 如果为 `True`，则输入和输出张量的形状为 (batch, seq, feature)。默认值：`False` (seq, batch, feature)。
- **norm_first** ([*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)) – 如果为 `True`，编码器和解码器层将在其他注意力层和前馈操作之前执行 LayerNorm，否则在其后执行。默认值：`False` (之后)。
- **bias** ([*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)) – 如果设置为 `False`，`Linear` 和 `LayerNorm` 层将不会学习加性偏置。默认值：`True`。

