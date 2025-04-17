# 交叉熵损失函数 

## 0. 问题背景

交叉熵损失函数（Cross Entropy Loss）作为在计算机视觉中用得最多的(没有之一)的损失函数，从定义到实践以及常常遇到的问题出发，来详细解读。**衡量两个概率分布或者集合之间的“距离”或者“相似性”的指标，如果这个指标可以概率化（即可导）那么就可以作为损失函数，而不同的损失函数其实本质就是使用了不同的衡量两个概率分布之间相似性的指标。**

------

## 1. 什么是 Cross Entropy Loss?

交叉熵损失函数是从信息编码理论启发得来的，交叉熵 $H(P,Q)$ 指的是在真实分布是 $P$，但我们用另一个分布 $Q$ 来编码时的平均信息量：

$$
H(P, Q) = - \sum_x P(x) \log Q(x)
$$

> 表示：用 $Q$ 编码 $P$ 时的”实际信息开销“，聪明的你已经注意到**交叉熵是不对等的，也就是说 $P$ 和 $Q$ 交换位置计算出来的交叉熵不相等。**

如果我使用 $P$ 本身来编码 $P$ 得到的是什么呢？
恭喜你发明了 **熵（Entropy）**，就可以表示这个事件本身的一个不确定性：
$$
H(P) = - \sum_x P(x) \log P(x)
$$

> 表示：按照真实分布 $P$ 自己来编码，需要的最少信息量。

如果我使用交叉熵减去熵得到的是什么呢？
恭喜你发明了**KL 散度（Kullback-Leibler Divergence）**，可以表示使用不同的 $Q$ 来编码 $P$ 需要的额外的信息量：
$$
\begin{align*} D_{KL}(P \| Q) &= \sum_x P(x) \log \frac{P(x)}{Q(x)} \\ &= \sum_x P(x) \left[ \log P(x) - \log Q(x) \right] \\ &= \sum_x P(x) \log P(x) - \sum_x P(x) \log Q(x) \\ &= -H(P) + H(P, Q) \\ &= H(P, Q) - H(P) \end{align*}
$$

> 表示：用 $Q$ 编码 $P$ 时的”额外信息开销“。

其实深度学习中我们需要的就是这样的”额外信息开销“来作为损失函数，不同的预测值对应不同的 $KL$散度，最小化 $KL$散度从而达到最优效果，等于0时表示预测值完全和真实值一样。又因为 $H(P)$ 是固定的。所以最小化 $KL$散度 = 最小化 $H(P, Q)$ 。
因为 $H(P, Q)$ 公式更加简单，所以交叉熵也成了深度学习中标准的损失函数。

## 2. CE Loss的优缺点

- 优点：计算简单直观，快速收敛。
- 缺点：公平的对待分布中的每一个值，所以**在不平衡的数据中更多关注多数类**。

## 3. 在 Pytorch 中使用 CE Loss

PyTorch 提供了两个核心函数用于处理交叉熵损失：

| 函数                     | 用途                                 | 注意事项                          |
| ------------------------ | ------------------------------------ | --------------------------------- |
| `nn.BCELoss`             | 二分类，用在 **sigmoid 后** 的概率上 | 输入必须是 `sigmoid` 输出         |
| `nn.BCEWithLogitsLoss` ✅ | 二分类，**自动带 sigmoid**（推荐）   | 输入是 raw logits                 |
| `nn.CrossEntropyLoss` ✅  | 多分类（含 softmax + log）           | 输入是 raw logits，标签是类别索引 |

✅ 二分类：使用 `BCEWithLogitsLoss`

> 对应二分类任务，标签为 0 或 1，模型输出一个标量 logits。

🔧 示例：

```python
import torch
import torch.nn as nn

# 模拟输出（logits）和标签
logits = torch.tensor([[0.8], [-1.2], [0.1]])  # shape: [batch, 1]
labels = torch.tensor([[1.], [0.], [1.]])      # shape: [batch, 1]

# 推荐用 BCEWithLogitsLoss（内部自动做 sigmoid）
criterion = nn.BCEWithLogitsLoss()
loss = criterion(logits, labels)
print("Binary classification loss:", loss.item())
```

✅ 特点：

- 输入是 **未经过 sigmoid 的 raw logits**

- 内部会做：

  ```python
  loss = -[y * log(sigmoid(x)) + (1 - y) * log(1 - sigmoid(x))]
  ```

------

✅ 多分类：使用 `CrossEntropyLoss`

> 用于多类别分类任务，输出维度为 `[batch_size, num_classes]`，标签为 `[batch_size]` 的类别索引。

🔧 示例：

```python
import torch
import torch.nn as nn

# 模拟输出（logits），每行代表一个样本的 [class1, class2, class3]
logits = torch.tensor([[2.0, 0.5, 0.3],
                       [0.2, 1.5, 0.1],
                       [1.0, 0.9, 1.2]])  # shape: [3, 3]
labels = torch.tensor([0, 1, 2])           # shape: [3]

# CrossEntropyLoss 自动做 softmax + log + NLL
criterion = nn.CrossEntropyLoss()
loss = criterion(logits, labels)
print("Multiclass classification loss:", loss.item())
```

✅ 特点：

- 输入是 logits（未做 softmax）

- 内部做：

  ```python
  loss = -log(softmax(logits)[true_class])
  ```

------

## 4. 使用技巧

- 在 ` nn.CrossEntropyLoss()`中具有`weight`和`label_smoothing`参数：

> weight （Tensor，可选） – 为每个类分配的手动重新缩放权重。 如果给定，则必须是大小为 num_class 且浮点数类型 的 Tensor

> label_smoothing （float， 可选） - [0.0， 1.0] 中的浮点数。指定平滑的程度，其中 0.0 表示不平滑。目标值成为原始真实分布 和均匀分布的混合。默认值0.0

- 在`nn.BCEWithLogitsLoss()`中有`pos_weight`参数 （非`weight`）：

> pos_weight (Tensor, 可选)  - [C]，每个类一个权重，$loss=−[pos_weight⋅y⋅log(σ(x))+(1−y)⋅log(1−σ(x))]$ 
>
> 一个小坑：`pos_weight=0` 并不是让这一类“忽略”，只是让这一类中的正类（这里面涉及到我们平时说的[多类和多标签](.\multi_class&multi_label.md)的区别）的损失变为 0，**负类损失还是会计算**。

