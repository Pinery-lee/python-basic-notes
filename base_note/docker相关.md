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

