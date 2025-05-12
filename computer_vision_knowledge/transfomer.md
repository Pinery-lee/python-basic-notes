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

### 2.1 `nn.Transfomer`的