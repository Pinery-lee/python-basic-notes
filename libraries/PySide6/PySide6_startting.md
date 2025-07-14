# 从零开始使用PySide6

## 0. 问题背景

最近需要把训练好的模型部署成.exe的形式交付，领导的要求是界面又得支持很多功能、好看、现代，遂选择PySide6作为开发GUI的框架，那我们现在开始吧。

## 1.什么是PySide6，跟PyQt6有啥区别？

PySide6 和 PyQt6 都是 Python 语言的 Qt 6 绑定，用于开发图形用户界面（GUI）。它们都基于 Qt 6 框架，但在授权、开发者支持和使用方式上存在一些重要区别和联系。

1. **底层框架相同**：两者都基于 Qt 6 框架，功能类似（如窗口、按钮、信号槽机制等）。
2. **功能对等**：提供的 API 大致相同，基本都支持 Qt 的主要模块，如 QtWidgets、QtCore、QtGui 等。
3. **使用方式类似**：界面开发的语法、流程基本一致，可以互相参考代码。
4. **可以用 Qt Designer 设计界面**：都支持将 `.ui` 文件转换成 Python 代码使用。

| 项目          | PySide6                               | PyQt6                                  |
| ------------- | ------------------------------------- | -------------------------------------- |
| 开发者/维护者 | **Qt 公司官方**（The Qt Company）     | **Riverbank Computing（个人/小团队）** |
| 授权协议      | **LGPL v3**                           | **GPL v3 或 商业授权（需付费）**       |
| 安装方式      | `pip install pyside6`                 | `pip install pyqt6`                    |
| 是否开源      | 是                                    | 是（但 PyQt 的 LGPL 不可用）           |
| 商业使用限制  | 较宽松（LGPL 允许动态链接后闭源发布） | 商用需购买授权，GPL 不适合闭源项目     |
| Qt 官方支持   | 是                                    | 否                                     |
| 包结构/模块名 | 比 PyQt 更贴近 C++ Qt 的命名风格      | 命名风格稍有不同                       |
| API 差异      | 少量，例如 `Signal` 的导入方式不同等  | 也有少量差异                           |
| 文档支持      | 官方文档参考 Qt C++/Python            | 有自己文档，也可以参考 Qt 官方文档     |

------

选择建议：

- **做开源项目**：二者都可以使用；
- **做商业闭源项目**：
  - 选择 **PySide6**（LGPL）更合适；
  - 使用 **PyQt6** 需要购买商业授权；
- **官方支持倾向**：Qt 官方主要推广 PySide6。

## 2. 环境配置

简单的开始可参考官方教程[Getting Started - Qt for Python](https://doc.qt.io/qtforpython-6/gettingstarted.html)

本来想在之前已有的环境中安装PySide6，结果报错：

```python
Found conflicts! Looking for incompatible packages.
This can take several minutes.  Press CTRL-C to abort.
failed

UnsatisfiableError: The following specifications were found
to be incompatible with the existing python installation in your environment:

Specifications:

  - pyside6 -> python[version='>=3.10,<3.11.0a0|>=3.11,<3.12.0a0|>=3.9,<3.10.0a0|>=3.12,<3.13.0a0']

Your python: python=3.8.18
```

那就新建一个虚拟环境吧...此处略去

```python
conda create -n PySide6 python pyside6
```

测试一下：没问题

```python
import PySide6.QtCore

print(PySide6.__version__)
print(PySide6.QtCore.__version__)
```

```python
6.7.2
6.7.3
```

## 3. 新建一个`Hello World!`界面

- 新建一个`.py`文件: 通过点击随机展示多种不同的打招呼语言。

```python
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui


class MyWidgets(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hello = ["Hallo Welt", "Hei maailma", "你好哇！"]
        self.button = QtWidgets.QPushButton("请点击！")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)  # type: ignore
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.rand_show_hw)

    @QtCore.Slot()
    def rand_show_hw(self):
        self.text.setText(random.choice(self.hello))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidgets()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
    
```

## 4. 必须掌握的核心概念

### 4.1 信号与槽（Signals and Slots）机制

 —— **信号（signal）像是一根电缆，发出电流；槽（slot）就像一个接口，等待信号连接进来。**

| 概念               | 含义                                                 |
| ------------------ | ---------------------------------------------------- |
| **信号（Signal）** | 一个事件发生时发出的通知（比如按钮被点击）           |
| **槽（Slot）**     | 一个可以接收信号并作出反应的函数（比如响应按钮点击） |
| `connect()`        | 建立"信号触发 → 槽函数执行"的连接                    |

工作机制：

- **信号是对象的成员（通常用 Qt 提供的 Signal 定义）**：例如`self.button.clicked`就是一个类变量`ClassVar[Signal]`

- **当某个条件触发时，信号会发出（emit）**：`Signal`带有`emit()`方法

- **如果有槽与该信号连接，就会自动调用对应的函数**：槽函数使用装饰器`@QtCore.Slot()`显示标识

需要注意的是：不加`@Slot()`程序也能运行，但是加了会规避很多潜在风险，推荐使用：

| 优势          | 原因                                                         |
| ------------- | ------------------------------------------------------------ |
| 更高性能      | 被注册为原生 Qt 槽，避免运行时反射，减少开销                 |
| 更高稳定性    | 防止 PySide6 引用错误，尤其是在**多线程**或 C++/Python 混用场景 |
| 内存友好      | 避免一些垃圾回收引用计数问题，比如死循环引用                 |
| 支持 QML 调用 | 如果你写 QML + Python 交互，**不加 `@Slot` 是无法从 QML 调用的！** |
| 明确表达语义  | 代码阅读性更好，开发者一眼能看出哪些是槽函数                 |

### 4.2  对象系统与父子结构

**——万物皆对象，在Qt中格外明显，一个app从上到下都是对象，构成了一个对象系统，而其中的父子关系可以使得很方便管理整个app。**

- 在 Qt（包括 PySide6）中，所有 UI 元素都继承自 `QObject`（比如 `QWidget`, `QPushButton`, `QLabel`, `QVBoxLayout` 等）。
- Qt中分为显式和隐式两种方式来建立父子关系。
- 父对象销毁时，子对象也会自动销毁，无需手动管理。

显示指定：子对象通过`parent`参数指定期父对象

```python
self.layout = QtWidgets.QVBoxLayout(self)
```

隐式指定：Qt自动设置

```python
self.button = QtWidgets.QPushButton("请点击！")
self.layout = QtWidgets.QVBoxLayout(self) 
# text 和 button 虽然你创建时没传 parent，但在加到 layout 时，会自动设置 parent = MyWidgets。注意text的父对象不是layout.
self.layout.addWidget(self.button)
```

> `QLayout` 并不是控件的 parent，而只是负责“管理”它们的位置和尺寸。控件的真正 parent 是这个 layout 所附着的 widget。

### 4.3 事件与 QApplication

**——人机的交互就是事件。`QApplication`是整个GUI应用程序的主控类。**

① 什么是 **事件（Event）**？

> 事件就是“发生了一件事”，比如你点击了鼠标、按下了键盘、窗口需要重绘、定时器到点了……

在 Qt 中，每个事件是一个对象，比如：

- `QMouseEvent`：鼠标点击
- `QKeyEvent`：键盘按下
- `QPaintEvent`：窗口需要重绘
- `QCloseEvent`：用户请求关闭窗口

这些事件会被 **自动生成**，比如用户点击了按钮，系统就会把这个动作变成 `QMouseEvent`类。

② 什么是 **事件循环（Event Loop）**？

> 事件循环就是一个“永不退出的 while 循环”，它不停地“等事件 → 收事件 → 派发事件”。运行了一个软件，就是开启了一个事件循环。

在 Qt 中，`QApplication.exec()` 启动这个循环：

```python
app = QtWidgets.QApplication(sys.argv)  # 一般没有参数，所以可以传一个[]
...
sys.exit(app.exec())   # 启动事件循环
```

③ 什么是 **事件调度（Event Dispatching）**？

> Qt 收到事件后，会找到正确的对象和处理函数来处理它。

这个过程叫事件调度（或事件分发）：

- 鼠标事件来了 → Qt 判断鼠标在哪个控件上 → 把事件传给那个控件
- 然后 Qt 调用这个控件的 `mousePressEvent(event)` 方法

④`QApplication`

- 所有 Qt 应用都必须有一个 `QApplication` 实例，它负责事件调度

| 功能             | 说明                             |
| ---------------- | -------------------------------- |
| 启动事件循环     | `app.exec()` 启动整个程序运行    |
| 管理全局设置     | 主题、字体、剪贴板、系统信号等   |
| 管理顶层窗口     | 所有窗口都挂在 `QApplication` 下 |
| 派发事件         | 它是事件分发的总调度器           |
| 管理应用生命周期 | 退出、关闭、崩溃管理等           |

```python
app = QtWidgets.QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
```

这段代码背后的流程是：

1. 创建 `QApplication`：准备运行 Qt 程序
2. 创建窗口并显示：窗口被注册到 Qt 对象系统中
3. 调用 `exec()`：开始事件循环（程序开始响应用户）
4. 用户操作 → Qt 转成事件 → 派发到正确的对象
5. 用户关闭窗口 → `exec()` 退出 → `sys.exit()` 返回

### 4.4 资源文件系统

Qt 的资源文件系统（**Qt Resource System**）是一种将非代码资源（如图像、图标、UI文件、样式表等）**嵌入到程序可执行文件**中的机制。它在开发跨平台应用时非常有用，因为这样可以不依赖文件路径，确保资源在所有平台上都能被访问。

* 把资源文件打包进 `.py` 中，不再依赖外部路径；
* 在代码中用 `:/前缀/路径` 的方式访问资源；
* 避免部署时遗漏文件，提高程序可移植性。

Qt 的资源文件系统基于 `.qrc` 文件。

#### 4.4.1 创建`resources.qrc`

```xml
<!DOCTYPE RCC><RCC version="1.0">
<qresource prefix="/images">
    <file>icons/icon1.png</file>
    <file>icons/icon2.png</file>
</qresource>
<qresource prefix="/qss">
    <file>style/main.qss</file>
</qresource>
</RCC>
```

* `<qresource prefix="/images">`：指定资源前缀；
* `<file>`：添加相对路径的文件。

#### 4.4.2 使用 `pyrcc6` 将 `.qrc` 编译为 Python 文件（PySide6）

```bash
pyrcc6 resources.qrc -o resources_rc.py
```

> 这一步使得所有的文件以二进制的方式被打包到py文件中

然后在代码中引入：

```python
import resources_rc
```

#### 4.4.3 在代码中使用资源

```python
label.setPixmap(QPixmap(":/images/icon1.png"))
```

> 注意 `:/` 是必须的，表示这是从资源系统中读取，而不是文件系统。

| 优点                             | 缺点                            |
| -------------------------------- | ------------------------------- |
| 程序不依赖外部资源路径，打包简单 | 每次更新资源都要重新编译 `.qrc` |
| 资源统一管理                     | 资源嵌入后可执行文件体积变大    |
| 跨平台一致性强                   | 运行时不能动态修改资源内容      |

集成 qss 样式、icon、图片 等资源完全可以放在一起。

### 4.5 布局管理

在 Qt（包括 PyQt/PySide）中，**布局管理（Layout Management）** 是 GUI 开发中非常重要的一部分，它控制着控件的位置、大小和排列方式，让界面既美观又响应式（随窗口大小变化自动适配）。

#### 4.5.1 为什么需要布局管理？

如果你只用 `.move()` 和 `.resize()` 手动放置控件，一旦窗口大小改变、控件内容变化，界面就容易错乱。布局管理器可以：

- 自动排列控件；
- 自动处理控件间的间距和边距；
- 自动响应窗口缩放；
- 简化代码、提升可维护性。

#### 4.5.2 常见布局类（Layout Classes）

| 布局类           | 中文     | 控件排列方向       | 常见用途           |
| ---------------- | -------- | ------------------ | ------------------ |
| `QHBoxLayout`    | 水平布局 | 左到右             | 工具栏、按钮行     |
| `QVBoxLayout`    | 垂直布局 | 上到下             | 页面主体、表单列表 |
| `QGridLayout`    | 网格布局 | 行列排列           | 表格、表单         |
| `QFormLayout`    | 表单布局 | 标签+控件成对排列  | 表单编辑界面       |
| `QStackedLayout` | 堆叠布局 | 一次只显示一个控件 | 页面切换、Tab 切换 |

#### 4.5.3 重要方法和属性

1. `addWidget(widget)`

向布局中添加一个控件。

2. `addLayout(layout)`

向布局中嵌套另一个布局（可以构建复杂布局结构）。

3. `addStretch(stretch=0)`

添加一个可伸缩的空白区域，用于撑开空间。

4. `setSpacing(pixels)`

设置控件之间的**间距**（控件之间的空隙）。

5. `setContentsMargins(left, top, right, bottom)`

设置布局的**外边距**，也就是布局与其边界控件之间的空隙。

#### 4.5.4 控件与布局的关系

在 Qt 中，每个控件都可以拥有一个布局管理器。布局本身并不显示，它只是管理其内部控件的位置。

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

window = QWidget()
layout = QVBoxLayout(window)  # 给 window 设置布局
layout.addWidget(QPushButton("按钮1"))
layout.addWidget(QPushButton("按钮2"))
```

#### 4.5.5 嵌套布局的例子

```python
mainLayout = QVBoxLayout()

# 顶部按钮行（水平）
topLayout = QHBoxLayout()
topLayout.addWidget(QPushButton("左"))
topLayout.addWidget(QPushButton("右"))

# 中间主区域
centerWidget = QTextEdit()

mainLayout.addLayout(topLayout)
mainLayout.addWidget(centerWidget)

window.setLayout(mainLayout)
```

#### 4.5.6 伸缩因子（Stretch Factors）

```python
layout.addWidget(widget, stretch=1)
layout.addStretch(2)
```

- 控件/伸缩区域所占空间的比例由 `stretch` 决定；
- 比如两个控件 stretch 分别是 1 和 2，前者占总宽度的 1/3，后者占 2/3。

#### 4.5.7 控件的尺寸策略

虽然布局负责排列控件，但控件本身的 `sizeHint()` 和 `sizePolicy()` 会影响其在布局中的表现：

- `setFixedSize(w, h)`：固定大小；
- `setMinimumSize()` / `setMaximumSize()`：设置尺寸限制；
- `sizePolicy()`：设置控件能否拉伸、压缩、保持原样。

例如：

```python
button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
```

表示：**水平方向可拉伸、垂直方向固定。**

------

## 📌 小结

| 概念                      | 作用               |
| ------------------------- | ------------------ |
| 布局类                    | 控制子控件如何排列 |
| `addWidget` / `addLayout` | 添加控件或子布局   |
| `setSpacing`              | 控件之间的距离     |
| `setContentsMargins`      | 整体边距           |
| 嵌套布局                  | 构建复杂界面       |
| `stretch`                 | 控制控件拉伸比例   |
| `sizePolicy`              | 控件是否允许拉伸   |







### 4️⃣ 常见控件（Widgets）

掌握基础控件是写 UI 的前提，包括但不限于：

| 控件                           | 作用           |
| ------------------------------ | -------------- |
| `QLabel`                       | 显示文本或图片 |
| `QPushButton`                  | 按钮           |
| `QLineEdit`                    | 单行文本输入   |
| `QTextEdit`                    | 多行文本编辑器 |
| `QCheckBox` / `QRadioButton`   | 选择项         |
| `QComboBox`                    | 下拉列表       |
| `QTableWidget` / `QTreeWidget` | 表格和树形数据 |
| `QDialog` / `QMessageBox`      | 弹窗           |

------

### 5️⃣ 布局管理（Layouts）

- 不要使用绝对坐标定位，用布局器管理控件位置：

  ```python
  layout = QVBoxLayout()
  layout.addWidget(button)
  self.setLayout(layout)
  ```

- 常见布局：

  - `QVBoxLayout`（垂直）
  - `QHBoxLayout`（水平）
  - `QGridLayout`（网格）
  - `QFormLayout`（表单）

------

### 6️⃣ Qt Designer 与 `.ui` 文件（可选）

- Qt 提供图形化设计工具 **Qt Designer**，生成 `.ui` 文件。
- 可用 `PySide6.QtUiTools.QUiLoader` 或 `pyside6-uic` 工具加载 `.ui` 文件为 Python 类。

------

### 7️⃣ 资源管理（资源文件 `.qrc`）

- 用 `.qrc` 文件组织图像、图标等静态资源，并通过 `qresource` 系统访问：

  ```python
  QPixmap(":/images/icon.png")
  ```

- 使用 `pyside6-rcc` 编译为 Python 模块。

------

### 8️⃣ 事件处理（事件系统）

- 可以重写控件的事件函数来定制行为：

  ```python
  def mousePressEvent(self, event):
      print("Clicked")
  ```

- 常见事件：键盘、鼠标、绘图、焦点等。

------

### 9️⃣ 自定义控件与继承

- 可以继承现有控件来自定义行为：

  ```python
  class MyButton(QPushButton):
      def mouseDoubleClickEvent(self, event):
          print("Double clicked")
  ```

------

### 🔟 跨线程通信（用 `QThread` + 信号）

- GUI 更新必须在主线程中完成。
- 使用 `QThread` + 信号机制实现安全跨线程通信。

------

## ✅ Bonus：模块结构与命名空间

PySide 模块按功能划分：

| 模块                         | 说明                               |
| ---------------------------- | ---------------------------------- |
| `PySide6.QtWidgets`          | 所有 GUI 控件                      |
| `PySide6.QtCore`             | 核心功能（信号槽、定时器、线程等） |
| `PySide6.QtGui`              | 图形、事件、字体、图标等           |
| `PySide6.QtNetwork`          | 网络功能                           |
| `PySide6.QtWebEngineWidgets` | 嵌入 Web 引擎视图                  |
| `PySide6.QtSql`              | 数据库支持                         |
| `PySide6.QtMultimedia`       | 音视频处理                         |

------

