# 池化Pooling

## 0. 问题背景

池化作为CNN架构的模型中的常见层，还是需要了解一下的。[torch.nn pooling layer — PyTorch 2.7 documentation](https://pytorch.org/docs/stable/nn.html#pooling-layers)

## 1. 什么是池化？

**[池化](https://www.jiqizhixin.com/graph/technologies/0a4cedf0-0ee0-4406-946e-2877950da91d)是一种下采样操作**，用于：

- 降低特征图尺寸（降低计算复杂度），这是最主要的目的
- 保留主要特征（增强鲁棒性）
- 控制过拟合（减少参数）

它通常**跟在卷积层后面**。

![池化示意](https://upload.wikimedia.org/wikipedia/commons/e/e9/Max_pooling.png)

上图是在单个通道中最为简单的，池化核大小为2，步长为2的最大池化示意图（即取最大值，其他值舍去，所以从信息论的角度也可以认为是一种有损的压缩技术）。

## 2. 常见池化类型（名字都长得像，别搞混）

| 名称             | PyTorch 层名                                    | 说明                                  |
| ---------------- | ----------------------------------------------- | ------------------------------------- |
| **最大池化**     | `nn.MaxPool2d`                                  | 取区域最大值                          |
| **平均池化**     | `nn.AvgPool2d`                                  | 取区域平均值                          |
| **自适应池化**   | `nn.AdaptiveAvgPool2d` / `nn.AdaptiveMaxPool2d` | 指定输出大小，不看输入大小            |
| **全局平均池化** | `AdaptiveAvgPool2d(1)`                          | 输出变成 `(N, C, 1, 1)`，常用于分类头 |
| **分数最大池化** | `nn.FractionalMaxPool2d`                        | 用概率控制下采样，较少用              |
| **P-范数池化**   | `nn.LPPool2d                                    | p阶范数形式的 pooling                 |

##  3. PyTorch 示例代码对比

### 3.1 最大池化（Max Pooling）

- 核内取最大值

```python
import torch
import torch.nn as nn

x = torch.tensor([[[[1., 2., 3., 4.],
                    [5., 6., 7., 8.],
                    [9.,10.,11.,12.],
                    [13.,14.,15.,16.]]]])

pool = nn.MaxPool2d(kernel_size=2, stride=2)
print(pool(x))
```

结果：

```
tensor([[[[ 6.,  8.],
          [14., 16.]]]])
```

### 3.2 平均池化（Avg Pooling）

- 核内取平均值

```python
pool = nn.AvgPool2d(kernel_size=2, stride=2)
print(pool(x))
```

结果：

```
tensor([[[[3.5, 5.5],
          [11.5, 13.5]]]])
```

### 3.3 自适应池化（Adaptive Pooling）

- **根据你指定的输出大小自动计算 kernel size 和 stride**，来完成池化操作的。

```python
import torch
import torch.nn as nn

x = torch.tensor([[[[1., 2., 3., 4.],
                    [5., 6., 7., 8.],
                    [9.,10.,11.,12.],
                    [13.,14.,15.,16.]]]])
# pool = nn.AdaptiveAvgPool2d((3, 4))
pool = nn.AdaptiveMaxPool2d((3, 4))  # 不管输入尺寸，输出就是 3x4，torch内部自动算
print(pool(x))
```

```python
tensor([[[[ 5.,  6.,  7.,  8.],
          [ 9., 10., 11., 12.],
          [13., 14., 15., 16.]]]])
```

### 3.4 全局平均池化 （Global Average Pooling）

- 输出的H×W是1×1，常用于代全连接层

```python
import torch
import torch.nn as nn

x = torch.tensor([[[[1., 2., 3., 4.],
                    [5., 6., 7., 8.],
                    [9.,10.,11.,12.],
                    [13.,14.,15.,16.]]]])

pool = nn.AdaptiveAvgPool2d((1, 1))  # 就是全局平均池化
print(pool(x))
```

```python
tensor([[[[8.5000]]]])
```

### 3.5 分数最大池化 （Fractional Max Pooling）

- 最大池化是按固定窗口划分图像，分数最大池化是根据目标输出大小动态决定滑窗方式，还带点轻微随机性。

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# 创建输入张量，形状为 (1, 1, 7, 7)
x = torch.arange(49, dtype=torch.float32).reshape(1, 1, 7, 7)
print("输入：\n", x)

# 普通最大池化：kernel=2, stride=2
maxpool = nn.MaxPool2d(kernel_size=2, stride=2)
out_max = maxpool(x)
print("\nMaxPool2d 输出：\n", out_max)

# 分数最大池化：目标输出为 (1, 1, 3, 3)
fracpool = nn.FractionalMaxPool2d(kernel_size=2, output_size=(3, 3))
out_frac = fracpool(x)
print("\nFractionalMaxPool2d 输出：\n", out_frac)
```

```python
输入：
 tensor([[[[ 0.,  1.,  2.,  3.,  4.,  5.,  6.],
          [ 7.,  8.,  9., 10., 11., 12., 13.],
          [14., 15., 16., 17., 18., 19., 20.],
          [21., 22., 23., 24., 25., 26., 27.],
          [28., 29., 30., 31., 32., 33., 34.],
          [35., 36., 37., 38., 39., 40., 41.],
          [42., 43., 44., 45., 46., 47., 48.]]]])

MaxPool2d 输出：
 tensor([[[[ 8., 10., 12.],
          [22., 24., 26.],
          [36., 38., 40.]]]])

FractionalMaxPool2d 输出：
 tensor([[[[ 8., 10., 13.],
          [29., 31., 34.],
          [43., 45., 48.]]]])
```

### 3.6 P-范数池化 （LP Pooling, Power-average Pooling)

LP池化（**Lp Pooling**）是一种**通用的池化操作**，它是 **最大池化（Max Pooling）** 和 **平均池化（Average Pooling）** 的一种推广形式。它通过引入一个参数 `p`，来控制聚合特征的方式。

 数学表达式：

给定一个池化窗口内的值是 `x₁, x₂, ..., xₙ`，Lp池化的计算方式如下：

$$
\text{LpPool}(x) = \left( \frac{1}{n} \sum_{i=1}^{n} |x_i|^p \right)^{\frac{1}{p}}
$$

其中：

- `n` 是池化窗口内的元素个数
- `p` 是一个正实数（常见值：1、2、∞）

🎯 特殊情况说明：

- **当 `p = 1` 时**，变成 **求和池化（等价于平均池化）**

$$
  \text{LpPool}_1(x) = \frac{1}{n} \sum |x_i|
$$

- **当 `p = 2` 时**，是 **平方平均池化**，对噪声鲁棒性更强。

$$
  \text{LpPool}_2(x) = \left( \frac{1}{n} \sum x_i^2 \right)^{1/2}
$$

- **当 `p → ∞` 时**，近似为 **最大池化（Max Pooling）**

$$
  \text{LpPool}_p(x) = \max(x)
$$

```python
import torch
import torch.nn as nn

x = torch.tensor([[[[1., 2., 3., 4.],
                    [5., 6., 7., 8.],
                    [9.,10.,11.,12.],
                    [13.,14.,15.,16.]]]])

pool = nn.LPPool2d(1, kernel_size=2, stride=2)
print(pool(x))
```

```python
tensor([[[[14., 22.],
          [46., 54.]]]])
```

- L1范数就是和

------

## 4. 实用建议（经验总结）

- 🚀 卷积层后常用 `MaxPool2d(kernel_size=2, stride=2)` 快速压缩
- 🤖 分类任务最后用 `AdaptiveAvgPool2d(1)` + `Flatten` 接 `Linear`
- 📏 输入大小不固定时，用 `Adaptive*` 系列更灵活
- ❗ 不要把池化当成“越多越好”，信息丢失严重。比如图像 512x512 → 连续 5 次 2x2 池化，就变成 16x16，几乎啥都没了
- 🎯 池化不增加通道数，只对空间（H, W）操作，不改变 `C`。如果通道数需要调整，用 `Conv2d(1x1)` 更合理

