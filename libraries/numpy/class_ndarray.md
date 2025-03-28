# ndarray

### 解释 NumPy 的 Array Objects（数组对象）

NumPy 提供了一种 N 维数组类型，即 **ndarray**（N-dimensional array），用于存储相同类型的元素。数组中的每个元素可以通过 N 个整数索引来访问。例如，在二维数组中，可以使用 `arr[i, j]` 访问某个元素。

由以下类实现

```python
numpy.ndarray
```

#### **1. ndarrays 的特性**

- **同质性（Homogeneous）**：所有元素的数据类型必须相同，每个元素在内存中占据相同大小的存储空间，并且存储格式一致。
- **数据类型对象（data-type object）**：每个 `ndarray` 都会关联一个数据类型对象（dtype），该对象定义数组元素的存储方式。例如，可以是整数（int）、浮点数（float）或自定义数据结构。
- **数组标量类型（array scalar types）**：当从 `ndarray` 中提取单个元素时，该元素会变成一个 NumPy 的标量对象。例如，如果 `arr` 是一个 `ndarray`，那么 `arr[0]` 可能是 `numpy.int32` 或 `numpy.float64`，而不是普通的 Python `int` 或 `float`。

#### **2. NumPy 数组的三大核心组成**

文中提到的 **三大核心对象** 可以用一个概念图表示：

1. **ndarray（数组对象）**：存储数据，并提供索引、运算等功能。
2. **数据类型对象（dtype）**：描述数组中每个元素的存储格式（大小、类型）。
3. **数组标量（array scalar）**：当提取单个元素时，它会变成 NumPy 的一个标量类型，而不是 Python 原生的 `int`、`float` 等。

### 详细解释三大核心对象

**1. `ndarray`（N 维数组）**

- 这是 NumPy 的核心数据结构，表示一个多维数组。
- 由 **header（头部信息）** 和 **数据块** 组成：
  - **header**：存储数组的元数据，例如数组的形状（shape）、数据类型（dtype）等。
  - **数据块**：实际存储数组元素，每个元素占据固定大小的内存。

**2. `data-type`（数据类型对象）**

- `dtype` 描述数组中每个元素的存储方式，包括：
  - 数据类型（如 `int32`、`float64`）
  - 每个元素占据的字节数
  - 数据的字节顺序（大端或小端）
  - 结构化数据的字段信息（如 `dtype=[('x', float), ('y', int)]`）

**3. `array scalar`（数组标量）**

- 当访问 `ndarray` 中的某个元素时（如 `arr[i]`），NumPy 会返回一个 **数组标量对象**，而不是 Python 的 `int` 或 `float`。
- 这个数组标量仍然保持 `ndarray` 中定义的数据类型，使得计算更高效。

