[Modules API - Qt for Python](https://doc.qt.io/qtforpython-6/api.html#pyside-api)

最核心的模块有三个，分别是`PySide6.Core`、`PySide6.QtGUI`、`PySide6.QtWidgets`

上述三个是基础模块，但是是属于`Widgets`派系

另一个派系就是`QML/QtQuick`，`QtQuick/QML` 是一个完全独立的 `UI` 架构，为了保持架构清晰、模块独立、渲染现代化、支持声明式开发，`Qt` 没有把它塞进 `QtWidgets/QtGui`，而是设计成 `QtQml` + `QtQuick` 两个独立模块。

其中四个核心模块是：`PySide6.QtQML`、`PySide6.QtQuick`、`PySide6.QtQuickControls`、`PySide6.QtQuickWidgets`

## 1.`PySide6.Core`

核心非 GUI 功能，如事件循环、日期时间、文件操作、多线程、信号与槽等。

## 2.`PySide6.GUI`

图形处理、字体、颜色、图标、QPainter、图形视图框架。

## 3.`PySide6.QtWidgets`

所有标准 GUI 控件，如按钮、窗口、对话框、布局管理等.



------

### ✅ QtGui vs QtWidgets 的区别

| 项目           | QtGui                                                        | QtWidgets                                                    |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **主要职责**   | 提供底层图形支持、事件系统和绘图引擎                         | 提供“部件”（控件）系统，例如按钮、窗口、布局等               |
| **是否依赖**   | 是 QtWidgets 的底层依赖                                      | 构建在 QtGui 之上，封装了可交互的 GUI 控件                   |
| **包含内容**   | `QPainter`, `QFont`, `QColor`, `QPixmap`, `QImage`, `QKeyEvent`, `QMouseEvent`, `QIcon`, `QClipboard` 等 | `QWidget`, `QPushButton`, `QLabel`, `QMainWindow`, `QDialog`, `QLayout` 等 |
| **用途定位**   | 绘图、图像处理、事件处理、2D 图形、图标资源管理              | 应用级 UI 构建，基于控件的界面开发                           |
| **直接可用性** | 更偏底层，通常需要与 QWidget 或 QWindow 配合使用             | 面向开发者的高级 UI 构建模块                                 |

------

### 🤔 为什么 Qt 要这样设计？

Qt 之所以把 `QtGui` 和 `QtWidgets` 分开，是为了 **模块化、可维护性** 和 **可扩展性**。背后有几个核心考虑：

------

#### 1. **职责单一（SRP）**

- `QtGui` 负责“渲染和事件”，是图形基础设施。
- `QtWidgets` 提供更高级的交互组件，是 UI 框架的一种实现方式。
- 这样 `QtGui` 可以服务于多个前端系统（包括 QtQuick、OpenGL、Widgets 等）。

------

#### 2. **支持多种 UI 技术**

Qt 除了支持传统的 Widgets，还支持：

- **QML/QtQuick（声明式 UI）**：完全不使用 `QtWidgets`，但依赖 `QtGui`。
- **OpenGL 渲染**：也仅需 `QtGui`。
- 因此把 `Widgets` 单独拆出，可以让 `QtGui` 成为通用绘图基础。

------

#### 3. **降低耦合性**

- 把控件（如按钮）和绘图逻辑分开，避免一改动全改。
- 比如你可以用 `QPainter` 单独绘图而不依赖任何控件。

------

#### 4. **方便移植和优化**

- 模块分离便于 Qt 对每个部分独立优化和升级，比如：
  - Qt 6 中 QtQuick 使用了全新的 GPU 渲染引擎（依赖 QtGui），但 QtWidgets 沿用原有机制。

------

### 🧠 总结

- `QtGui` 是 **底层绘图和事件系统**；
- `QtWidgets` 是 **基于 QWidget 的传统控件系统**；
- 它们分开，是为了职责清晰、便于维护和支持多种 UI 技术路线；
- 在 PySide6 中你会经常 `QtWidgets + QtGui` 一起用，一个是框架，一个是基础。

## 4.`PySide6.QML/QtQuick`

| 模块              | 作用                    | 常用类/功能                                | 常见用途         |
| ----------------- | ----------------------- | ------------------------------------------ | ---------------- |
| `QtQML`           | 连接 Python 与 QML 引擎 | `QQmlApplicationEngine`, `qmlRegisterType` | 启动和控制 QML   |
| `QtQuick`         | 提供图形基础设施        | `Rectangle`, `Image`, 动画类               | 构建 QML UI      |
| `QtQuickControls` | 提供常用 UI 控件        | `Button`, `Slider`, `ApplicationWindow`    | 构建交互界面     |
| `QtQuickWidgets`  | 让 QML 嵌入 QWidget     | `QQuickWidget`                             | 混合旧项目和 QML |

在 PySide6 中，涉及 **Web 相关功能** 的子模块主要有以下两个：

------

## 5. `PySide6.QtWebEngineWidgets`

> 提供 **嵌入 Chromium 浏览器引擎** 到 Qt 应用中的能力，适合展示网页、前端界面或 Web App。

### 🔧 常用类：

| 类名                 | 说明                                |
| -------------------- | ----------------------------------- |
| `QWebEngineView`     | 主体 Web 浏览器控件，可加载网页     |
| `QWebEnginePage`     | 表示页面，可控制导航、JS 执行等     |
| `QWebEngineProfile`  | 浏览器配置（缓存、cookies、权限等） |
| `QWebEngineSettings` | 启用 JS、插件、缩放等设置           |
| `QWebEngineScript`   | 注入 JS 脚本                        |

### ✅ 示例：

```python
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView

app = QApplication([])

view = QWebEngineView()
view.load("https://www.qt.io")
view.show()

app.exec()
```

------

## 6. `PySide6.QtWebChannel`

> 用于在 **QML 或 HTML 页面 与 Python 后端之间建立双向通信** 的模块。

### ✨ 作用：

- 可以让网页中的 JavaScript 调用 Python 对象的方法
- 也可以让 Python 主动调用网页中的 JS 函数

### 🔧 常用类：

| 类名             | 说明                                                   |
| ---------------- | ------------------------------------------------------ |
| `QWebChannel`    | 核心通道类，桥接 JS 与 Python                          |
| `QObject` 派生类 | 你要导出的对象，需含有 `@Slot`, `@Property`, `@Signal` |

## 

| 模块名                       | 功能                       | 是否支持 JS 通信 | 推荐用途                 |
| ---------------------------- | -------------------------- | ---------------- | ------------------------ |
| `PySide6.QtWebEngineWidgets` | 嵌入网页、浏览器控件       | ✅                | 桌面软件展示网页内容     |
| `PySide6.QtWebChannel`       | Web 与 Python 对象互通桥梁 | ✅                | 前后端通信（Hybrid App） |

[Qt Modules Supported by Qt for Python - Qt for Python](https://doc.qt.io/qtforpython-6/modules.html)