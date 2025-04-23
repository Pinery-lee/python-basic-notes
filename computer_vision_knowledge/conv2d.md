# 二维卷积Conv2d

## 0. 问题背景

作为CNN架构的最核心的模块，必须要掌握其理论，实现，使用和使用注意事项。[Conv2d — PyTorch 2.6 documentation](https://pytorch.org/docs/stable/generated/torch.nn.Conv2d.html#torch.nn.Conv2d)

## 1. 什么是二维卷积？

二维卷积是通过滑动一个小的卷积核（滤波器）在图像上，对局部区域进行加权求和，从而提取图像的空间特征的操作。

![动图](https://picx.zhimg.com/50/v2-15fea61b768f7561648dbea164fcb75f_720w.webp?source=1def8aca)

这是一个非常简单的二维卷积，简单的点在于输入图像的维度只有1维（而一般是RGB三维）、输出的维度也只有一维（除了二分类的输出层，一般不会为1维）、步长为1,、卷积核大小只有3*3、没有对原图像做padding、没有添加偏置。上述的torch实现是：

```python
import torch
import torch.nn as nn

# 创建输入
x = torch.tensor([[[[0,  0, 75, 80, 80],
                    [0, 75, 80, 80, 80],
                    [0, 75, 80, 80, 80],
                    [0, 70, 75, 80, 80],
                    [0,  0,  0,  0,  0]]]], dtype=torch.float32)

# 创建卷积层
conv = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=3, stride=1, padding=0, bias=False)

# 手动设置权重为图中的核
kernel = torch.tensor([[[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]]], dtype=torch.float32)

conv.weight.data = kernel.unsqueeze(0)  # shape [1, 1, 3, 3]

# 执行卷积
output = conv(x)

print(output)
```

```python
tensor([[[[ 155.,   85.,    5.],
          [ -15.,  -15.,   -5.],
          [-230., -315., -320.]]]], grad_fn=<ConvolutionBackward0>)
```

## 2. `torch.nn.Conv2d`的参数解释

### 📌 构造函数原型：

```python
torch.nn.Conv2d(
    in_channels, 
    out_channels, 
    kernel_size, 
    stride=1, 
    padding=0, 
    dilation=1, 
    groups=1, 
    bias=True, 
    padding_mode='zeros'
)
```

------

### 📖 参数解释：

- **in_channels（输入通道数）**：
   类型：`int`
   输入图像的通道数。例如，RGB 图片是 3 通道，灰度图是 1 通道。
   👉 通常等于前一层的输出通道数。
- **out_channels（输出通道数）**：
   类型：`int`
   卷积之后产生的通道数，也就是该层卷积核的数量。每个卷积核会生成一个输出通道。
   👉 这个值决定了输出特征图的“厚度”。
- **kernel_size（卷积核大小）**：
   类型：`int` 或 `tuple (height, width)`
   卷积核的尺寸。例如 `3` 表示 `3x3` 的核。
   👉 控制感受野的大小。
- **stride（步长）**：
   类型：`int` 或 `tuple`，默认值为 `1`
   卷积核滑动的步长，决定输出特征图的尺寸。
   👉 大步长会减小输出尺寸（类似下采样）。
- **padding（填充）**：
   类型：`int`、`tuple` 或 `str`，默认值为 `0`
   在输入图像四周添加的像素层数。
   👉 通常使用 `padding=1` 保证输出尺寸与输入相同（在 stride=1 的情况下）。
- **dilation（空洞长度）**：
   类型：`int` 或 `tuple`，[1, H/W)，默认值为 `1`
   控制卷积核内部元素之间的间距。1表示卷积核中间不插入0，n表示在每一行或列中间插入**（dilation-1）**个0
   👉 用于 **空洞卷积**，增大感受野而不增加参数量。
- **groups（分组卷积）**：
   类型：`int`，默认值为 `1`
   控制输入输出之间的连接方式：
  - `groups=1`：普通卷积，每个输入通道连接每个输出通道；
  - `groups=in_channels=out_channels`：**depthwise 卷积**，每个输入通道使用一个卷积核独立处理；
  - 其他情况：**分组卷积**（如 ResNeXt 中使用）。
- **bias（是否添加偏置项）**：
   类型：`bool`，默认值为 `True`
   是否为每个输出通道添加一个可学习的偏置项。
   👉 如果使用了 BatchNorm，通常设置为 `False`。
- **padding_mode（填充方式）**：
   类型：`str`，默认值为 `'zeros'`
   填充的模式，可选值有：
  - `'zeros'`：用 0 填充（默认）
  - `'reflect'`：反射填充
  - `'replicate'`：复制边界值填充
  - `'circular'`：循环填充

## 3. 输入输出的张量形状变化

- 输入：**$\left(N, C_{i n}, H_{i n}, W_{i n}\right)$ 或者 $\left(C_{i n}, H_{i n}, W_{i n}\right)$**, 注意是高H×宽W
- 输出：$\left(N, C_{\text {out }}, H_{\text {out }}, W_{\text {out }}\right)$ 或者 $\left(C_{\text {out }}, H_{\text {out }}, W_{\text {out }}\right)$

$$
\begin{aligned}
& H_{\text {out }}=\left\lfloor\frac{H_{\text {in }}+2 \times \text { padding }[0]-\text { dilation }[0] \times(\text { kernel-size }[0]-1)-1}{\text { stride }[0]}+1\right\rfloor \\
& W_{\text {out }}=\left\lfloor\frac{W_{\text {in }}+2 \times \text { padding }[1]-\text { dilation }[1] \times(\text { kernel-size }[1]-1)-1}{\text { stride }[1]}+1\right\rfloor
\end{aligned}
$$

$H_{\text {in }}+2 \times \text { padding }$ 是填充之后的原图大小，$\text { dilation }\times(\text { kernel-size }-1)+1$ 是真实卷积核的大小， $H_{\text {in }}+2 \times \text { padding }-\text { dilation } \times(\text { kernel-size }-1)-1$ 是这个卷积核能滑动的范围，所以卷积核能滑动的范围除以步长就是输出的维度，但是如果不能整除， 最后多余的几行/列不参与卷积！所以要加1然后向下取整。

实验：

```python
import torch
import torch.nn as nn

# 输入大小：6x6（不能被stride=2整除）
x = torch.arange(6 * 6, dtype=torch.float32).reshape(1, 1, 6, 6)
print("输入 x:")
print(x[0, 0])

# 卷积参数
conv = nn.Conv2d(
    in_channels=1,
    out_channels=1,
    kernel_size=3,
    stride=2,
    padding=1,
    bias=False
)

# 权重全设为1，方便验证求和区域
with torch.no_grad():
    conv.weight.fill_(1.0)

# 执行卷积
output = conv(x)
print("\n输出 shape:", output.shape)
print("输出结果:")
print(output[0, 0])
```

```python
输入 x:
tensor([[ 0.,  1.,  2.,  3.,  4.,  5.],
        [ 6.,  7.,  8.,  9., 10., 11.],
        [12., 13., 14., 15., 16., 17.],
        [18., 19., 20., 21., 22., 23.],
        [24., 25., 26., 27., 28., 29.],
        [30., 31., 32., 33., 34., 35.]])

输出 shape: torch.Size([1, 1, 3, 3])
输出结果:
tensor([[ 14.,  30.,  42.],
        [ 75., 126., 144.],
        [147., 234., 252.]], grad_fn=<SelectBackward0>)
```

###  输出解释

- 输入是 `6×6`，stride=2，padding=1，原图像大小就会变为6+2=8，卷积核大小为3，所有卷积核的滑动范围为5，每次滑动2，所以最后一行卷积不到，最后一行是padding行为0
- 根据输出公式：

$$
H_{\text{out}} = \left\lfloor \frac{H_{\text{in}} + 2 \times \text{padding} - (k - 1) - 1}{\text{stride}} + 1 \right\rfloor = \left\lfloor \frac{6 + 2 - 2 - 1}{2} + 1 \right\rfloor = \left\lfloor \frac{5}{2} + 1 \right\rfloor = 3
$$

- 对于结果第一列而言，14对应0的位置，1+6+7=14；75对应12的位置，6+7+12+13+18+19=75；147对应24的位置，18+19+24+25+30+31=147；最后的零行被舍弃不参与卷积。

所以输出的形状是 **3×3**

## 4. 卷积层的变量 Variables

- **weight**权重：可学习的权重，其实就是所有的卷积核合并为的一个张量。形状是 （out_channels, in_channels/groups, kernel_size[0], kernel_size[1]）。默认使用均匀分布初始化。
- **bias**偏置：可学习的偏置，形状是（out_channels），初始化同上。

## 5. groups 参数

如果设置了 `groups=g`，那么：

- 输入通道被分成 `g` 组，每组大小 = `in_channels // g`
- 输出通道也分 `g` 组，每组大小 = `out_channels // g`
- 每组内部独立卷积（不跨组）

所以`groups`的取值必须是[1, max(in_channels, out_channels)], 且必须能整除in_channels和out_channels

## 6. 常见的特殊形式

------

## ✅ 1. 标准卷积（Standard Convolution）

- `groups=1`（默认值）
- 每个输出通道连接所有输入通道

```python
import torch
import torch.nn as nn

# 输入大小：6x6（不能被stride=2整除）
x = torch.arange(6 * 6 * 3, dtype=torch.float32).reshape(1, 3, 6, 6)
print("输入 x:")
print(x[0])

# 卷积参数
conv = nn.Conv2d(
    in_channels=3,
    out_channels=1,
    kernel_size=3,
    bias=False,
    padding=1
)

# 权重全设为1，方便验证求和区域
with torch.no_grad():
    conv.weight.fill_(1.0)

# 执行卷积
output = conv(x)
print("\n输出 shape:", output.shape)
print("输出结果:")
print(output[0])
```

```python
输入 x:
tensor([[[  0.,   1.,   2.,   3.,   4.,   5.],
         [  6.,   7.,   8.,   9.,  10.,  11.],
         [ 12.,  13.,  14.,  15.,  16.,  17.],
         [ 18.,  19.,  20.,  21.,  22.,  23.],
         [ 24.,  25.,  26.,  27.,  28.,  29.],
         [ 30.,  31.,  32.,  33.,  34.,  35.]],

        [[ 36.,  37.,  38.,  39.,  40.,  41.],
         [ 42.,  43.,  44.,  45.,  46.,  47.],
         [ 48.,  49.,  50.,  51.,  52.,  53.],
         [ 54.,  55.,  56.,  57.,  58.,  59.],
         [ 60.,  61.,  62.,  63.,  64.,  65.],
         [ 66.,  67.,  68.,  69.,  70.,  71.]],

        [[ 72.,  73.,  74.,  75.,  76.,  77.],
         [ 78.,  79.,  80.,  81.,  82.,  83.],
         [ 84.,  85.,  86.,  87.,  88.,  89.],
         [ 90.,  91.,  92.,  93.,  94.,  95.],
         [ 96.,  97.,  98.,  99., 100., 101.],
         [102., 103., 104., 105., 106., 107.]]])

输出 shape: torch.Size([1, 1, 6, 6])
输出结果:
tensor([[[ 474.,  720.,  738.,  756.,  774.,  522.],
         [ 765., 1161., 1188., 1215., 1242.,  837.],
         [ 873., 1323., 1350., 1377., 1404.,  945.],
         [ 981., 1485., 1512., 1539., 1566., 1053.],
         [1089., 1647., 1674., 1701., 1728., 1161.],
         [ 762., 1152., 1170., 1188., 1206.,  810.]]],
       grad_fn=<SelectBackward0>)
```

- 474=0+1+6+7+36+37+42+43+72+73+78+79

## ✅ 2.  深度可分离卷积（Depthwise Convolution）

- `groups=in_channels`, out_channels将至少为1*groups
- 每个输入通道对应一个卷积核，**不混通道**

```python
import torch
import torch.nn as nn

# 输入大小：6x6（不能被stride=2整除）
x = torch.arange(6 * 6 * 3, dtype=torch.float32).reshape(1, 3, 6, 6)
print("输入 x:")
print(x[0])

# 卷积参数
conv = nn.Conv2d(
    in_channels=3,
    out_channels=3,
    kernel_size=3,
    bias=False,
    padding=1,
    groups=3
)

# 权重全设为1，方便验证求和区域
with torch.no_grad():
    conv.weight.fill_(1.0)

# 执行卷积
output = conv(x)
print("\n输出 shape:", output.shape)
print("输出结果:")
print(output[0])
```

```python
输入 x:
tensor([[[  0.,   1.,   2.,   3.,   4.,   5.],
         [  6.,   7.,   8.,   9.,  10.,  11.],
         [ 12.,  13.,  14.,  15.,  16.,  17.],
         [ 18.,  19.,  20.,  21.,  22.,  23.],
         [ 24.,  25.,  26.,  27.,  28.,  29.],
         [ 30.,  31.,  32.,  33.,  34.,  35.]],

        [[ 36.,  37.,  38.,  39.,  40.,  41.],
         [ 42.,  43.,  44.,  45.,  46.,  47.],
         [ 48.,  49.,  50.,  51.,  52.,  53.],
         [ 54.,  55.,  56.,  57.,  58.,  59.],
         [ 60.,  61.,  62.,  63.,  64.,  65.],
         [ 66.,  67.,  68.,  69.,  70.,  71.]],

        [[ 72.,  73.,  74.,  75.,  76.,  77.],
         [ 78.,  79.,  80.,  81.,  82.,  83.],
         [ 84.,  85.,  86.,  87.,  88.,  89.],
         [ 90.,  91.,  92.,  93.,  94.,  95.],
         [ 96.,  97.,  98.,  99., 100., 101.],
         [102., 103., 104., 105., 106., 107.]]])

输出 shape: torch.Size([1, 3, 6, 6])
输出结果:
tensor([[[ 14.,  24.,  30.,  36.,  42.,  30.],
         [ 39.,  63.,  72.,  81.,  90.,  63.],
         [ 75., 117., 126., 135., 144.,  99.],
         [111., 171., 180., 189., 198., 135.],
         [147., 225., 234., 243., 252., 171.],
         [110., 168., 174., 180., 186., 126.]],

        [[158., 240., 246., 252., 258., 174.],
         [255., 387., 396., 405., 414., 279.],
         [291., 441., 450., 459., 468., 315.],
         [327., 495., 504., 513., 522., 351.],
         [363., 549., 558., 567., 576., 387.],
         [254., 384., 390., 396., 402., 270.]],

        [[302., 456., 462., 468., 474., 318.],
         [471., 711., 720., 729., 738., 495.],
         [507., 765., 774., 783., 792., 531.],
         [543., 819., 828., 837., 846., 567.],
         [579., 873., 882., 891., 900., 603.],
         [398., 600., 606., 612., 618., 414.]]], grad_fn=<SelectBackward0>)
```

- 14 = 0+1+6+7; 158 = 36+37+42+43; 302 = 72+73+78+79

## ✅ 3.  分组卷积（Group Convolution）

- `1 < groups < in_channels`
- 比如 `groups=2`：把输入分成两组，每组用独立卷积核处理

```python
import torch
import torch.nn as nn

# 输入大小：6x6（不能被stride=2整除）
x = torch.arange(6 * 6 * 4, dtype=torch.float32).reshape(1, 4, 6, 6)
print("输入 x:")
print(x[0])

# 卷积参数
conv = nn.Conv2d(
    in_channels=4,
    out_channels=2,
    kernel_size=3,
    bias=False,
    padding=1,
    groups=2
)

# 权重全设为1，方便验证求和区域
with torch.no_grad():
    conv.weight.fill_(1.0)

# 执行卷积
output = conv(x)
print("\n输出 shape:", output.shape)
print("输出结果:")
print(output[0])
```

```python
输入 x:
tensor([[[  0.,   1.,   2.,   3.,   4.,   5.],
         [  6.,   7.,   8.,   9.,  10.,  11.],
         [ 12.,  13.,  14.,  15.,  16.,  17.],
         [ 18.,  19.,  20.,  21.,  22.,  23.],
         [ 24.,  25.,  26.,  27.,  28.,  29.],
         [ 30.,  31.,  32.,  33.,  34.,  35.]],

        [[ 36.,  37.,  38.,  39.,  40.,  41.],
         [ 42.,  43.,  44.,  45.,  46.,  47.],
         [ 48.,  49.,  50.,  51.,  52.,  53.],
         [ 54.,  55.,  56.,  57.,  58.,  59.],
         [ 60.,  61.,  62.,  63.,  64.,  65.],
         [ 66.,  67.,  68.,  69.,  70.,  71.]],

        [[ 72.,  73.,  74.,  75.,  76.,  77.],
         [ 78.,  79.,  80.,  81.,  82.,  83.],
         [ 84.,  85.,  86.,  87.,  88.,  89.],
         [ 90.,  91.,  92.,  93.,  94.,  95.],
         [ 96.,  97.,  98.,  99., 100., 101.],
         [102., 103., 104., 105., 106., 107.]],

        [[108., 109., 110., 111., 112., 113.],
         [114., 115., 116., 117., 118., 119.],
         [120., 121., 122., 123., 124., 125.],
         [126., 127., 128., 129., 130., 131.],
         [132., 133., 134., 135., 136., 137.],
         [138., 139., 140., 141., 142., 143.]]])

输出 shape: torch.Size([1, 2, 6, 6])
输出结果:
tensor([[[ 172.,  264.,  276.,  288.,  300.,  204.],
         [ 294.,  450.,  468.,  486.,  504.,  342.],
         [ 366.,  558.,  576.,  594.,  612.,  414.],
         [ 438.,  666.,  684.,  702.,  720.,  486.],
         [ 510.,  774.,  792.,  810.,  828.,  558.],
         [ 364.,  552.,  564.,  576.,  588.,  396.]],

        [[ 748., 1128., 1140., 1152., 1164.,  780.],
         [1158., 1746., 1764., 1782., 1800., 1206.],
         [1230., 1854., 1872., 1890., 1908., 1278.],
         [1302., 1962., 1980., 1998., 2016., 1350.],
         [1374., 2070., 2088., 2106., 2124., 1422.],
         [ 940., 1416., 1428., 1440., 1452.,  972.]]],
       grad_fn=<SelectBackward0>)
```

- 172 = 0+1+6+7+36+37+42+43（第一组）; 748 = 72+73+78+79+108+109+114+115（第二组）

## ✅ 4. 1x1 卷积（Pointwise Convolution）

- `kernel_size=1`
- 常用于**通道维度压缩或扩展**

```python
import torch
import torch.nn as nn

# 输入大小：6x6（不能被stride=2整除）
x = torch.arange(6 * 6 * 3, dtype=torch.float32).reshape(1, 3, 6, 6)
print("输入 x:")
print(x[0])

# 卷积参数
conv = nn.Conv2d(
    in_channels=3,
    out_channels=1,
    kernel_size=1,
    bias=False,
)

# 权重全设为1，方便验证求和区域
with torch.no_grad():
    conv.weight.fill_(1.0)

# 执行卷积
output = conv(x)
print("\n输出 shape:", output.shape)
print("输出结果:")
print(output[0])
```

```python
输入 x:
tensor([[[  0.,   1.,   2.,   3.,   4.,   5.],
         [  6.,   7.,   8.,   9.,  10.,  11.],
         [ 12.,  13.,  14.,  15.,  16.,  17.],
         [ 18.,  19.,  20.,  21.,  22.,  23.],
         [ 24.,  25.,  26.,  27.,  28.,  29.],
         [ 30.,  31.,  32.,  33.,  34.,  35.]],

        [[ 36.,  37.,  38.,  39.,  40.,  41.],
         [ 42.,  43.,  44.,  45.,  46.,  47.],
         [ 48.,  49.,  50.,  51.,  52.,  53.],
         [ 54.,  55.,  56.,  57.,  58.,  59.],
         [ 60.,  61.,  62.,  63.,  64.,  65.],
         [ 66.,  67.,  68.,  69.,  70.,  71.]],

        [[ 72.,  73.,  74.,  75.,  76.,  77.],
         [ 78.,  79.,  80.,  81.,  82.,  83.],
         [ 84.,  85.,  86.,  87.,  88.,  89.],
         [ 90.,  91.,  92.,  93.,  94.,  95.],
         [ 96.,  97.,  98.,  99., 100., 101.],
         [102., 103., 104., 105., 106., 107.]]])

输出 shape: torch.Size([1, 1, 6, 6])
输出结果:
tensor([[[108., 111., 114., 117., 120., 123.],
         [126., 129., 132., 135., 138., 141.],
         [144., 147., 150., 153., 156., 159.],
         [162., 165., 168., 171., 174., 177.],
         [180., 183., 186., 189., 192., 195.],
         [198., 201., 204., 207., 210., 213.]]], grad_fn=<SelectBackward0>)
```

- 108 = 0+36+72

## ✅ 5. 空洞卷积（Dilated Convolution）

![动图](https://pica.zhimg.com/v2-9c531569460c694db396a7530d8e5ffc_b.webp)

- `dilation > 1`：扩大感受野，不加参数

```python
import torch
import torch.nn as nn

# 输入大小：6x6（不能被stride=2整除）
x = torch.arange(6 * 6 * 3, dtype=torch.float32).reshape(1, 3, 6, 6)
print("输入 x:")
print(x[0])

# 卷积参数
conv = nn.Conv2d(
    in_channels=3,
    out_channels=1,
    kernel_size=3,
    bias=False,
    dilation=2
)

# 权重全设为1，方便验证求和区域
with torch.no_grad():
    conv.weight.fill_(1.0)

# 执行卷积
output = conv(x)
print("\n输出 shape:", output.shape)
print("输出结果:")
print(output[0])
```

```python
输入 x:
tensor([[[  0.,   1.,   2.,   3.,   4.,   5.],
         [  6.,   7.,   8.,   9.,  10.,  11.],
         [ 12.,  13.,  14.,  15.,  16.,  17.],
         [ 18.,  19.,  20.,  21.,  22.,  23.],
         [ 24.,  25.,  26.,  27.,  28.,  29.],
         [ 30.,  31.,  32.,  33.,  34.,  35.]],

        [[ 36.,  37.,  38.,  39.,  40.,  41.],
         [ 42.,  43.,  44.,  45.,  46.,  47.],
         [ 48.,  49.,  50.,  51.,  52.,  53.],
         [ 54.,  55.,  56.,  57.,  58.,  59.],
         [ 60.,  61.,  62.,  63.,  64.,  65.],
         [ 66.,  67.,  68.,  69.,  70.,  71.]],

        [[ 72.,  73.,  74.,  75.,  76.,  77.],
         [ 78.,  79.,  80.,  81.,  82.,  83.],
         [ 84.,  85.,  86.,  87.,  88.,  89.],
         [ 90.,  91.,  92.,  93.,  94.,  95.],
         [ 96.,  97.,  98.,  99., 100., 101.],
         [102., 103., 104., 105., 106., 107.]]])

输出 shape: torch.Size([1, 1, 2, 2])
输出结果:
tensor([[[1350., 1377.],
         [1512., 1539.]]], grad_fn=<SelectBackward0>)
```

- 1350 = 0+2+4+12+14+16+24+26+28 + 36+38+40+48+50+52+60+62+64 + 72+74+76+84+86+88+96+98+100

## ✅ 6. 跨步卷积（Strided Convolution）

[Strided Convolutions](https://www.baeldung.com/cs/neural-nets-strided-convolutions)

- 能降低计算复杂度，通过跳过像素，网络可以更高效地处理较大的图像
- 下采样用，效果等价于卷积 + pooling

```python
import torch
import torch.nn as nn

# 输入大小：6x6（不能被stride=2整除）
x = torch.arange(6 * 6 * 1, dtype=torch.float32).reshape(1, 1, 6, 6)
print("输入 x:")
print(x[0])

# 卷积参数
conv = nn.Conv2d(
    in_channels=1,
    out_channels=1,
    kernel_size=3,
    bias=False,
    stride=2
)

# 权重全设为1，方便验证求和区域
with torch.no_grad():
    conv.weight.fill_(1.0)

# 执行卷积
output = conv(x)
print("\n输出 shape:", output.shape)
print("输出结果:")
print(output[0])
```

```python
输入 x:
tensor([[[ 0.,  1.,  2.,  3.,  4.,  5.],
         [ 6.,  7.,  8.,  9., 10., 11.],
         [12., 13., 14., 15., 16., 17.],
         [18., 19., 20., 21., 22., 23.],
         [24., 25., 26., 27., 28., 29.],
         [30., 31., 32., 33., 34., 35.]]])

输出 shape: torch.Size([1, 1, 2, 2])
输出结果:
tensor([[[ 63.,  81.],
         [171., 189.]]], grad_fn=<SelectBackward0>)
```

- 63 = 0+1+2+6+7+8+12+13+14；171 = 12+13+14+18+19+20+24+25+26；**最后一行不参与卷积**

## 📌 总结对比表

| 类型           | groups       | kernel_size | dilation | stride | 应用场景              |
| -------------- | ------------ | ----------- | -------- | ------ | --------------------- |
| 标准卷积       | 1            | 任意        | 1        | 1      | 常规卷积操作          |
| 深度可分离卷积 | =in_channels | 任意        | 1        | 1      | MobileNet, 轻量模型   |
| 分组卷积       | >1           | 任意        | 1        | 1      | ResNeXt, 特征分组处理 |
| 1x1卷积        | 1            | 1           | 1        | 1      | 通道变换、瓶颈结构    |
| 空洞卷积       | 1            | 任意        | >1       | 1      | 语义分割，扩大感受野  |
| 跨步卷积       | 1            | 任意        | 1        | >1     | 下采样，替代 pooling  |

