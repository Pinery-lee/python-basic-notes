# Focal Loss

## 0. 问题背景

Focal Loss 基本每一个做计算机视觉的都会了解到，其核心思想是：让“难分类的样本”贡献更大的 loss，降低“容易分类的样本”的影响。是很好的应对样本不平衡问题的损失函数。

## 1. Focal Loss的定义

Focal loss 起源于[交叉熵损失函数CE_Loss](./CE_loss.md)

$$
\mathrm{CE}(p, y)=-\sum_{t=1}^C y_t \log \left(p_t\right)
$$

其中，$ C $ 是类别数，$p$ 是模型预测的每一类的概率，$ y $ 是真实标签(one-hot)，假设第 $ t $ 类是对应的类别，所以只有 $ y_t = 1 $ ，所以公式可以简化为：

$$
\mathrm{CE}(p, y) = -\log \left(p_t\right)
$$

Focal Loss 就是在交叉熵的基础上加了调节系数 $ -\alpha_t\left(1-p_t\right)^\gamma $：

$$
\mathrm{FL}(p, y)=-\alpha_t\left(1-p_t\right)^\gamma \log \left(p_t\right)
$$


