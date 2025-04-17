# 多类别 (multi-class) VS. 多标签 (multi-label)

## 0. 问题背景

我在查看 pytorch 的官方文档关于 [BCEWithLogitsLoss — PyTorch 2.6 documentation](https://pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html) 的时候，发现它给的例子如下：

```python
target = torch.ones([10, 64], dtype=torch.float32)  # 64 classes, batch size = 10
output = torch.full([10, 64], 1.5)  # A prediction (logit)
pos_weight = torch.ones([64])  # All weights are equal to 1
criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
criterion(output, target)  # -log(sigmoid(1.5))
```

我当时的疑惑就是为什么 target 是64类， 但却可以用二分类交叉熵损失函数`BCEWithLogitsLoss`呢？原因在于我混淆了多类别和多标签的区别

------

## 🧩 1. 四种分类任务全景图

| 类型                 | 说明                     | 标签                                    | 模型输出                       | 损失函数                                  |
| -------------------- | ------------------------ | --------------------------------------- | ------------------------------ | ----------------------------------------- |
| **二分类（单标签）** | 只有两类，互斥           | `[0]` / `[1]`                           | `[B]`（1个 logit） 或 `[B, 2]` | `BCEWithLogitsLoss` or `CrossEntropyLoss` |
| **多分类（单标签）** | 多个类，互斥             | `[0, 2, 1]`                             | `[B, C]` logits                | `CrossEntropyLoss`                        |
| **多标签二分类**     | 每个样本可有多个标签     | `[0,1,0,1,...]` (one-hot 多维)          | `[B, C]` logits                | `BCEWithLogitsLoss`                       |
| **多标签多分类**     | 每个标签本身是一个多分类 | 复杂结构，例如 `[class1: 2, class2: 0]` | 多头输出 `[B, C1], [B, C2]...` | 多个 `CrossEntropyLoss`                   |

------

## 🧠2. 判断标准 & 示例

### ✅ 1. **二分类（单标签）**

- 输出：`[B]` 或 `[B, 1]` logit（只预测正类得分）
- 标签：`[B]`，0 或 1
- 损失：`BCEWithLogitsLoss`

```python
output = model(x)           # shape: [B]
target = torch.tensor([0, 1, 1, 0])
loss = nn.BCEWithLogitsLoss()(output, target.float())
```

> 🔸 如果用了 `[B, 2]` 的输出（两个类），也可以用 `CrossEntropyLoss`。

------

### ✅ 2. **多分类（单标签）**

- 每个样本只能属于一个类别
- 输出：`[B, C]` logits
- 标签：`[B]`，整数类别索引
- 损失：`CrossEntropyLoss`

```python
output = model(x)           # shape: [B, C]
target = torch.tensor([0, 2, 1, 3])  # 每个样本属于哪一类
loss = nn.CrossEntropyLoss()(output, target)
```

------

### ✅ 3. **多标签（二分类）**

- 每个样本可能属于多个类别
- 输出：`[B, C]`，每个维度是一个类别
- 标签：`[B, C]`，0/1 表示该标签是否存在
- 损失：`BCEWithLogitsLoss`

```python
output = model(x)            # shape: [B, C]
target = torch.tensor([[1,0,1], [0,1,1]])  # 每类是否出现
loss = nn.BCEWithLogitsLoss()(output, target.float())
```

------

### ✅ 4. **多标签多分类**（较复杂,一般不常用）

- 每类标签是一个多分类问题
- 输出多个 heads，每个 head 是一个分类器
- 标签是多个类别索引，形如：`[batch, num_heads]`
- 通常用多个 `CrossEntropyLoss` 合并

```python
output1 = model_head1(x)    # shape: [B, C1]
output2 = model_head2(x)    # shape: [B, C2]
loss1 = nn.CrossEntropyLoss()(output1, target[:, 0])
loss2 = nn.CrossEntropyLoss()(output2, target[:, 1])
loss = loss1 + loss2
```

------

## 🔍 3. 如何自动判断该用哪个损失？

### 👇 可以通过标签 shape 判断：

```python
if target.ndim == 1:
    loss_fn = nn.CrossEntropyLoss()  # 多分类（单标签）
elif target.ndim == 2 and target.max() <= 1:
    loss_fn = nn.BCEWithLogitsLoss()  # 多标签（二分类）
```

------

## 🎓 4. 总结：快速判断表

| 任务         | 标签类型                | 模型输出      | 损失函数                |
| ------------ | ----------------------- | ------------- | ----------------------- |
| 二分类       | `[0,1]`                 | `[B]`         | `BCEWithLogitsLoss`     |
| 多分类       | `[0,1,2,...]`           | `[B, C]`      | `CrossEntropyLoss`      |
| 多标签分类   | `[[0,1,1,...]]`         | `[B, C]`      | `BCEWithLogitsLoss`     |
| 多标签多分类 | `[class1, class2, ...]` | 多个 `[B, C]` | 多个 `CrossEntropyLoss` |

------

更准确和深入的探讨可查看[Multiclass Classification vs Multi-label Classification | GeeksforGeeks](https://www.geeksforgeeks.org/multiclass-classification-vs-multi-label-classification/)

