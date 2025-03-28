# generic



![numpy标量结构图](https://numpy.org/doc/stable/_images/dtype-hierarchy.png)

有很多别名

------



### **1. Python 只有一种整数类型和浮点数类型**

在标准 Python 里：

- **整数类型（int）**：无论大小，Python 只有 `int` 这一种整数类型，它会自动扩展（不像 C 语言区分 `int`, `long`, `short` 等）。
- **浮点数类型（float）**：只有 `float` 一种类型，通常对应 C 语言的 `double`。

这样设计的好处是**简洁统一**，但缺点是**缺乏对底层存储和性能的精细控制**。对于科学计算，**数据存储方式和精度非常重要**，比如：

- 处理大规模数据时，存储空间很重要，可能希望用 `int8`（8 位整数）代替 `int64`（64 位整数）。
- 计算浮点数时，可能希望用 `float32`（32 位）提高计算速度，而不是 `float64`。

------

### **2. NumPy 提供 24 种新的基本数据类型**

NumPy 为了增强科学计算的能力，引入了 **基于 C 语言的更多数据类型**，比如：

- **整数类型**
  - `np.int8`（8 位整数，取值范围 -128 到 127）
  - `np.int16`（16 位整数，取值范围 -32,768 到 32,767）
  - `np.int32`（32 位整数）
  - `np.int64`（64 位整数）
- **浮点数类型**
  - `np.float16`（16 位浮点数）
  - `np.float32`（32 位浮点数，精度比 `float64` 低，但运算快）
  - `np.float64`（64 位浮点数，等价于 Python 的 `float`）
- **复数类型**
  - `np.complex64`（32 位浮点数的复数）
  - `np.complex128`（64 位浮点数的复数）
- **布尔类型**
  - `np.bool_`（存储 `True`/`False`，但占用 8 位）
- **灵活数据类型**
  - `np.str_`（固定长度字符串）
  - `np.bytes_`（固定长度字节串）
  - `np.void`（可以存储任意数据块）

这些类型**与 C 语言的数据类型相对应**，这样可以更高效地与 C/C++ 代码交互，同时也可以**节省内存，提高计算速度**。

------

### **3. 数组标量（Array Scalars）**

NumPy **不仅支持数组（ndarray）**，还提供了**数组标量（Array Scalars）**，它们与数组类似但表示单个数值。例如：

```python
import numpy as np

x = np.array([1, 2, 3], dtype=np.int32)  # 这是一个数组
y = x[0]  # 取出第一个元素
print(type(y))  # <class 'numpy.int32'>
```

`y` 不是 Python 的 `int`，而是 NumPy 的 `int32`，这是一种 **数组标量**，它保留了 `int32` 类型的信息。

这些 **数组标量（Array Scalars）**：

- **拥有和 `ndarray` 类似的方法**（比如 `.dtype`，`.item()`）。
- **与数组操作兼容**，避免标量和数组混用时出现不一致的行为。

例如：

```python
a = np.array([1, 2, 3], dtype=np.float32)
b = a[0]  # b 是 np.float32 标量
print(b * 2)  # 2.0（仍然是 float32，而不是 Python 的 float）
```

Python 的 `float` 默认是 `float64`，但 `b` 保持 `float32`，**避免类型转换，提高性能**。

------

### **4. NumPy 数据类型的层次结构**

NumPy 的数据类型可以按照 **继承关系** 组织成一个 **层次结构**（Hierarchy），例如：

```python
import numpy as np

x = np.float32(3.14)
print(isinstance(x, np.generic))  # True
print(isinstance(x, np.floating))  # True
print(isinstance(x, np.complexfloating))  # False
```

- `np.generic` 是所有 NumPy 标量类型的基类。
- `np.floating` 是所有浮点数类型（`float16`, `float32`, `float64`）的基类。
- `np.complexfloating` 是所有复数类型（`complex64`, `complex128`）的基类。

你可以使用 `isinstance(val, np.generic)` 检测 `val` 是否是 NumPy 标量：

```python
val = np.int32(42)
print(isinstance(val, np.generic))  # True
```

或者使用更具体的类型：

```python
print(isinstance(val, np.integer))  # True
print(isinstance(val, np.floating))  # False
```

这样可以**在不确定具体数据类型时，进行更泛化的类型判断**。

------

### **5. 主要优势**

NumPy 这样设计的好处包括：

1. **更高效**：比 Python 的 `int` 和 `float` 速度更快，且占用更少内存。
2. **兼容 C 语言**：可以与 C 语言数据类型对接，提高扩展性。
3. **支持更多数据类型**：允许更细粒度的控制（如 `float32` 比 `float64` 更节省内存）。
4. **数组与标量行为一致**：减少数据类型不匹配的 Bug。

------

### 6. **总结**

- Python **只有一种整数类型 (`int`) 和一种浮点数类型 (`float`)**，NumPy 提供 **更多精细的数据类型**（如 `int8`, `float32`）。
- NumPy **有 24 种数据类型**，大部分基于 C 语言的类型。
- NumPy **数组中的元素** 不是 Python 内置类型，而是 **NumPy 的标量类型（Array Scalars）**。
- **数组标量** 具有 `ndarray` 的属性，**减少标量和数组混用时的类型不一致问题**。
- NumPy **数据类型有层次结构**，可以用 `isinstance()` 判断类型。

这样，NumPy **兼顾了 Python 的易用性和 C 语言的高性能**，让科学计算既方便又高效！ 🚀