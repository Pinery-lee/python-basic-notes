# Docker

我是在windows上安装的docker desktop，所以相关知识是关于windows, WSL, docker, linux 等相关知识的总结。

### 我的 Docker Desktop 的版本

```
PS C:\Users\admin> docker --version
Docker version 28.4.0, build d8eb465
PS C:\Users\admin> wsl --version
WSL 版本: 2.6.1.0
内核版本: 6.6.87.2-1
WSLg 版本: 1.0.66
MSRDC 版本: 1.2.6353
Direct3D 版本: 1.611.1-81528511
DXCore 版本: 10.0.26100.1-240331-1435.ge-release
Windows: 10.0.26100.6584
```

### Docker 的 数据存放格式和位置

- 在设置 Settings -> Resources -> Advanced -> Disk image location 中，可以看到 Docker 的数据存放位置。

- 可以看到里面就两个文件 `DockerDesktopWSL\main\ext4.vhdx` 和 `DockerDesktopWSL\disk\docker_data.vhdx`。

- `ext4.vhdx`前者是 **Docker Desktop 自己的 Linux 系统盘**。里面是一个完整的 Linux 文件系统（ext4 格式），专门运行 Docker 守护进程（dockerd）和 Linux 相关的后台服务。

- `docker_data.vhdx`后者是 **Docker 的数据盘**。里面存放着 Docker 的镜像、容器、卷等数据。系统盘和数据盘分开，方便管理。

- 如果 C 盘够用，则放C盘，否则放 D 盘。

### Docker 核心概念

- **镜像（Image）**：Docker 镜像是一个只读的模板，里面包含了运行容器所需的一切环境和配置。

- **容器（Container）**：Docker 容器是一个运行中的镜像实例，可以被创建、启动、停止、删除。

### Dockerfile

- Dockerfile 是用来构建 Docker 镜像的文本文件，包含了一条条的指令来告诉 Docker 如何构建镜像。注意该文件没有后缀。

- 示例：

```
# 指定基础镜像，新构建的镜像将基于此镜像
FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

# 指定工作目录，后续的操作都在此目录下进行
WORKDIR /cropland_server

# 安装依赖，先 copy 进来 依赖配置项，再安装
COPY requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 拷贝代码 (这里不拷贝是可以volume挂载文件)
# COPY . .

# 暴露端口
EXPOSE 5000

# 指定容器创建时的默认命令。
CMD ["python", "app.py"]
```

- 其他命令：LABEL 添加镜像的元数据，使用键值对的形式。RUN	在构建过程中在镜像中执行命令。ENV 在容器内部设置环境变量。

- 主要是 `docker build` 和 `docker-compose build` 会使用到该文件。


### docker-compose.yml

- 是 Docker Compose 使用的配置文件（默认名字就叫 docker-compose.yml）。本质是一个 声明式的配置清单，用 YAML 格式写。用来描述：①要运行哪些服务（containers），②这些服务用什么镜像，③需要什么端口映射，④需要什么卷挂载，⑤网络、环境变量、启动命令等。

- 示例：  使用`docker-compose up` 运行 docker-compose.yml 中的如下配置：

```
version: "3.9"

services:
  flask-backend:
    build: ./flask
    ports:
      - "5000:5000"
    volumes:
      -./flask:/app

  node-frontend:
    build: ./node
    ports:
      - "3000:3000"
    volumes:
      -./node:/app
```

等同于：

```
docker run -d --name flask_backend -p 5000:5000 -v ./flask:/app flask_image
docker run -d --name node_frontend -p 3000:3000 -v ./node:/app node_image
```

### docker run 和 docker compose build 的区别

- `docker build`：单镜像构建命令，直接对 Docker 引擎操作，适合打包、发布、做复杂 buildx 操作。

- `docker compose build`：基于 docker-compose.yml 的多服务构建，负责按 Compose 配置为每个服务构建镜像并打 tag，适合项目化、多服务一键化开发/测试流程。

### docker run 和 docker-compose up 的区别

- `docker run`: 单容器命令，相当于用命令行参数（-p、-v、-e 等）把配置写死。适合临时测试或只需要启动一个容器的时候。

- `docker compose up`: 基于 docker-compose.yml，编排多个服务（可以是 N 个容器）的一键启动。适合项目开发/部署，因为配置都写在文件里，复现方便。

- `docker compose up` 能在没有构建镜像的时候，自动构建镜像并启动容器。`docker run` 本身不能构建镜像。

### docker-compose 和 docker compose 的区别

- `docker-compose up` = 旧版本（V1），现在基本就是个兼容别名。

- `docker compose up` = 新版本（V2），是 Docker 官方推荐用法。

