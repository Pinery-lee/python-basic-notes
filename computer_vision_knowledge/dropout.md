# Dropout

Dropout 是正则化的方法之一，本质上指的是在**训练期间**随机将某些张量元素归零的操作，从而抑制模型过拟合、增强泛化能力。

------

## 1. 为什么是在训练期间，推理阶段能不能？

Dropout 只在**训练阶段生效**，推理（inference）阶段是关闭的。
 原因在于，Dropout 的目的是在训练时通过随机遮挡一部分神经元，迫使模型不依赖某些特征，从而提升模型鲁棒性。而在推理阶段，我们希望模型利用所有学到的特征（强行Dropout会降低模型性能），因此需要**关闭 Dropout 并使用完整网络结构**，同时通过缩放激活值保持期望不变（例如 PyTorch 中自动处理缩放）。

------

## 2. 怎么确定哪些元素归零，哪些元素不归零？

Dropout 的归零机制是**随机的**，每次根据设置的概率 `p` 随机生成一个与输入张量相同形状的 **伯努利分布（Bernoulli）掩码**，其中：

- 以概率 `p` 将某个位置设为 0（即 Drop 掉该元素）；
- 以概率 `1-p` 将其保留，并在保留时将值除以 `1-p`（称为“反向缩放”，使期望一致）。

示意：

```python
mask = torch.bernoulli(torch.ones_like(x) * (1 - p))
out = x * mask / (1 - p)
```

------

## 3. 某些张量一般指的是什么张量？

Dropout 一般作用于**神经网络中的激活值（activations）张量**，即激活函数的结果，而不是权重或偏置：

- 对于全连接层，是对神经元输出（activation）进行 Drop；
- 对于卷积层，可以使用 **Spatial Dropout（Dropout2D）**，按通道将整个 feature map Drop 掉；
- 在 Transformer 等结构中也可用于 attention 层或 feed-forward 层之后（但要注意这里[dropout是对注意力权重张量进行的](.\computer_vision_knowledge\self_attention&multi-head attention.md)）。

------

## 4. 参数概率 p 如何生效？

`p` 是 Dropout 的超参数，表示**每个元素被“Drop”的概率**：

- 典型值如 0.1 ~ 0.5；
- 如果设置为 `p=0.5`，则训练时约一半的神经元激活被归零；
- 越深的网络，常常越需要较大的 p 值来防止过拟合；
- 但 Dropout 并非越大越好，过高会造成训练不稳定或欠拟合。

------

## 5. 示例说明

以 PyTorch 为例：

```python
import torch
import torch.nn as nn

drop = nn.Dropout(p=0.5)

x = torch.tensor([[1.0, 2.0, 3.0, 4.0]])
drop.train()  # 训练模式
print(drop(x))  # 随机 Drop 某些元素

drop.eval()  # 推理模式
print(drop(x))  # 输出不变，只做缩放
```

输出（可能类似）：

```
tensor([[0.0000, 4.0000, 6.0000, 0.0000]])  # 一半 Drop，另一半除以 0.5
tensor([[1.0000, 2.0000, 3.0000, 4.0000]])  # 推理时不 Drop
```

------

需要我配一张示意图展示 Dropout 的作用机制吗？