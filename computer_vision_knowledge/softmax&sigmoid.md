# softmax和sigmoid函数

## 0. 问题背景

softmax 和 sigmoid 适用场景不同，在计算机视觉中是必用的。

------

## 1. sigmoid

常说的s形函数。每个输出值是**独立**的，不会受到其他值的影响。所以它可以用于每个类别是“是/否”的独立判断（多标签二分类）

公式：

$$
\text sigmoid(x) = \frac{1}{1 + e^{-x}}
$$

输出范围：(0, 1)

典型用途：[二分类、多标签二分类](.\multi_class&multi_label.md)

## 2. softmax

是sigmoid 用于互斥的多分类的外推形式。每个输出值不是独立的，会受到其他值的约束，输出值总和为1.

公式：

$$
\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_{j} e^{x_j}}
$$

输出范围：(0, 1)

------

## 3. 实验

如果在二分类、多分类、多标签二分类中同时用sigmoid和softmax会发生什么？

```python
import torch
import torch.nn.functional as F

# 设置随机种子方便复现
torch.manual_seed(0)

print("="*40)
print("【1】二分类 (Binary Classification)")
logits_bin = torch.tensor([[1.2], [-1.2]])   # [B, 1]
targets_bin = torch.tensor([1.0, 0.0])   # [B]
print(torch.sigmoid(logits_bin))
print(F.softmax(logits_bin, dim=1))

print("\n" + "="*40)
print("【2】多分类 (Multi-Class Classification)")
# batch size = 1, num_classes = 3
logits_multi = torch.tensor([[2.0, 1.0, 0.1], [2.0, 1.0, 0.1]])  # [B, 3]
targets_multi = torch.tensor([[0.0, 1.0]])  # [B]
print(torch.sigmoid(logits_multi))
print(F.softmax(logits_multi, dim=1))

print("\n" + "="*40)
print("【3】多标签二分类 (Multi-Label Classification)")
logits_multilabel = torch.tensor([[1.5, -1.0, 0.3], [1.5, -1.0, 0.3]])  # [B, 3]
targets_multilabel = torch.tensor([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])  # [B, 3]

print(torch.sigmoid(logits_multilabel))
print(F.softmax(logits_multilabel, dim=1))
```

```python
========================================
【1】二分类 (Binary Classification)
tensor([[0.7685],
        [0.2315]])
tensor([[1.],
        [1.]])

========================================
【2】多分类 (Multi-Class Classification)
tensor([[0.8808, 0.7311, 0.5250],
        [0.8808, 0.7311, 0.5250]])
tensor([[0.6590, 0.2424, 0.0986],
        [0.6590, 0.2424, 0.0986]])

========================================
【3】多标签二分类 (Multi-Label Classification)
tensor([[0.8176, 0.2689, 0.5744],
        [0.8176, 0.2689, 0.5744]])
tensor([[0.7229, 0.0593, 0.2177],
        [0.7229, 0.0593, 0.2177]])
```

- 二分类：softmax 的分子分母相等，永远为1。禁用。
- 多分类：sigmoid 得到的所有输出概率类别之和将不等于1，如果后续使用argmax获取最大类别则不影响结果，如果使用概率阈值的话将会出现同是为多类的情况。慎用。
- 多标签二分类：softmax 将引入类别竞争，会使得非最大概率类的其他类的概率更低。慎用。

------

## 2. 什么时候用哪个？

| 类型   | 正确激活  | 正确损失       | 备注          |
| ------ | --------- | -------------- | ------------- |
| 二分类 | ✅ sigmoid | ✅ BCE          | ❌禁用softmax  |
| 多分类 | ✅ softmax | ✅ CrossEntropy | ⚠ 慎用sigmoid |
| 多标签 | ✅ sigmoid | ✅ BCE          | ⚠ 慎用softmax |
