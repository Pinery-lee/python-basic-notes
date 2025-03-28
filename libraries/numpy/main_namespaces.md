# Numpy main namespaces

### **NumPy 主命名空间（Main Namespaces）解释**

NumPy 的核心功能按模块化设计，主要分为多个**命名空间（namespaces）**，每个命名空间负责特定功能。以下是 NumPy 推荐的主要用户接口命名空间及其用途：

---

## **1. `numpy`（核心命名空间）**
**作用**：包含 NumPy 最基础、最常用的功能，如数组操作、数学运算等。  
**主要功能**：

- 数组创建（`np.array()`, `np.zeros()`, `np.ones()`）
- 数学运算（`np.sin()`, `np.exp()`, `np.sum()`）
- 数组操作（`np.reshape()`, `np.concatenate()`）  
**示例**：
```python
import numpy as np
arr = np.array([1, 2, 3])  # 创建数组
print(np.sum(arr))          # 计算总和
```

---

## **2. `numpy.exceptions`（异常处理）**
**作用**：定义 NumPy 特有的异常类型，用于错误处理。  
**常见异常**：
- `np.exceptions.AxisError`（轴索引错误）
- `np.exceptions.LinAlgError`（线性代数计算错误）  
**示例**：
```python
try:
    np.linalg.inv(np.zeros((2, 2)))  # 尝试对奇异矩阵求逆
except np.exceptions.LinAlgError:
    print("矩阵不可逆！")
```

---

## **3. `numpy.fft`（快速傅里叶变换）**
**作用**：提供离散傅里叶变换（DFT）和逆变换（IDFT）功能，用于信号处理、频谱分析等。  
**主要函数**：
- `np.fft.fft()`（快速傅里叶变换）
- `np.fft.ifft()`（逆变换）
- `np.fft.fftfreq()`（计算频率分量）  
**示例**：
```python
signal = np.array([1, 2, 1, 0])
spectrum = np.fft.fft(signal)  # 计算频谱
```

---

## **4. `numpy.linalg`（线性代数）**
**作用**：提供矩阵运算、特征值分解、解线性方程组等功能。  
**核心函数**：
- `np.linalg.inv()`（矩阵求逆）
- `np.linalg.eig()`（特征值分解）
- `np.linalg.solve()`（解线性方程组）  
**示例**：
```python
A = np.array([[1, 2], [3, 4]])
b = np.array([5, 6])
x = np.linalg.solve(A, b)  # 解 Ax = b
```

---

## **5. `numpy.polynomial`（多项式运算）**
**作用**：多项式拟合、求导、积分等操作。  
**子模块**：
- `np.polynomial.Polynomial`（标准多项式）
- `np.polynomial.Chebyshev`（切比雪夫多项式）  
**示例**：
```python
p = np.polynomial.Polynomial([1, 2, 3])  # 1 + 2x + 3x²
print(p.deriv())  # 求导：2 + 6x
```

---

## **6. `numpy.random`（随机数生成）**
**作用**：生成各种概率分布的随机数。  
**常用函数**：
- `np.random.rand()`（均匀分布）
- `np.random.normal()`（正态分布）
- `np.random.randint()`（整数随机数）  
**示例**：
```python
data = np.random.normal(0, 1, 100)  # 标准正态分布100个样本
```

---

## **7. `numpy.strings`（字符串操作）**
**作用**：提供向量化的字符串处理函数（类似 Python 的 `str` 方法）。  
**主要函数**：
- `np.strings.add()`（字符串拼接）
- `np.strings.upper()`（转大写）  
**示例**：
```python
arr = np.array(["hello", "numpy"])
print(np.strings.upper(arr))  # 输出 ["HELLO", "NUMPY"]
```

---

## **8. `numpy.testing`（测试工具）**
**作用**：提供单元测试和数组比较功能，用于验证 NumPy 代码的正确性。  
**常用函数**：
- `np.testing.assert_allclose()`（近似相等检查）
- `np.testing.assert_array_equal()`（数组完全匹配）  
**示例**：
```python
a = np.array([1.000001, 2.000002])
b = np.array([1.0, 2.0])
np.testing.assert_allclose(a, b, rtol=1e-5)  # 允许微小误差
```

---

## **9. `numpy.typing`（类型注解）**
**作用**：提供 NumPy 数组的类型注解支持，用于静态类型检查（如 `mypy`）。  
**主要类型**：
- `numpy.typing.NDArray`（泛型数组类型）
- `numpy.typing.DTypeLike`（数据类型注解）  
**示例**：
```python
from numpy.typing import NDArray
def compute_mean(arr: NDArray[np.float64]) -> float:
    return arr.mean()
```

---

### **总结**
| **命名空间**    | **主要用途**                   | **典型应用场景**       |
| --------------- | ------------------------------ | ---------------------- |
| `numpy`         | 核心数组和数学运算             | 通用数值计算           |
| `numpy.fft`     | 傅里叶变换和频谱分析           | 信号处理、音频分析     |
| `numpy.linalg`  | 线性代数（矩阵运算、求解方程） | 机器学习、物理模拟     |
| `numpy.random`  | 随机数生成                     | 蒙特卡洛模拟、数据采样 |
| `numpy.testing` | 单元测试和数值验证             | 代码质量保证           |
| `numpy.typing`  | 类型注解（静态类型检查）       | 大型项目开发           |

这些命名空间构成了 NumPy 的核心功能体系，用户可根据需求选择合适模块进行高效的科学计算。

