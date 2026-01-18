# Linux.do 刷帖助手 - 多平台打包指南

## Windows 版本

Windows 可执行文件请优先从 GitHub Releases 或 Actions 构建产物获取，文件名示例：
- `LinuxDoHelper-pyinstaller-<version>-windows-amd64.exe`
- `LinuxDoHelper-nuitka-windows-amd64.exe`

如需本地打包，请参考下文 PyInstaller/Nuitka 的命令并在 Windows 上执行。

---

## macOS 版本打包指南

### 环境准备

```bash
# 1. 安装 Python 3.8+
brew install python@3.11

# 2. 安装依赖
pip3 install -r requirements.txt
pip3 install pyinstaller

# 3. 安装 Chrome 浏览器
# 从 https://www.google.com/chrome/ 下载安装
```

### 打包命令

```bash
# 进入项目目录
cd /path/to/linuxdo

# 执行打包
pyinstaller --onefile --windowed \
    --name "LinuxDoHelper_v<version>_macOS" \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tkinter.scrolledtext \
    --hidden-import DrissionPage \
    --hidden-import pystray \
    --hidden-import PIL \
    --add-data "icon.ico:." \
    --clean --noconfirm \
    linux_do_gui.py

# 或者使用打包脚本
python3 build.py
```

### 输出文件
- `dist/LinuxDoHelper_v<version>_macOS` (可执行文件)

### 运行方式
```bash
# 赋予执行权限
chmod +x dist/LinuxDoHelper_v<version>_macOS

# 运行
./dist/LinuxDoHelper_v<version>_macOS
```

### macOS 安全提示
首次运行可能提示"无法验证开发者"，解决方法：
1. 系统偏好设置 → 安全性与隐私 → 通用
2. 点击"仍要打开"

---

## Linux 版本打包指南

### 环境准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-tk

# CentOS/RHEL
sudo yum install python3 python3-pip python3-tkinter

# Arch Linux
sudo pacman -S python python-pip tk

# 安装依赖
pip3 install -r requirements.txt
pip3 install pyinstaller

# 安装 Chrome 浏览器
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

### 打包命令

```bash
# 进入项目目录
cd /path/to/linuxdo

# 执行打包
pyinstaller --onefile --windowed \
    --name "LinuxDoHelper_v<version>_Linux" \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tkinter.scrolledtext \
    --hidden-import DrissionPage \
    --hidden-import pystray \
    --hidden-import PIL \
    --add-data "icon.ico:." \
    --clean --noconfirm \
    linux_do_gui.py

# 或者使用打包脚本
python3 build.py
```

### 输出文件
- `dist/LinuxDoHelper_v<version>_Linux` (可执行文件)

### 运行方式
```bash
# 赋予执行权限
chmod +x dist/LinuxDoHelper_v<version>_Linux

# 运行
./dist/LinuxDoHelper_v<version>_Linux
```

### Linux 注意事项
1. 需要图形界面环境 (X11/Wayland)
2. 如果使用 WSL，需要配置 X Server
3. 无头服务器无法运行 GUI 程序

---

## 通用注意事项

### 运行要求
1. **Chrome 浏览器**: 必须安装 Chrome 浏览器
2. **网络连接**: 需要能访问 linux.do
3. **代理设置**: 如需代理，在程序中配置

### 常见问题

#### Q: 程序启动后没有反应
A: 检查是否安装了 Chrome 浏览器

#### Q: 提示找不到 chromedriver
A: DrissionPage 会自动下载，确保网络通畅

#### Q: macOS 提示"已损坏，无法打开"
A: 执行 `xattr -cr /path/to/LinuxDoHelper_v<version>_macOS`

#### Q: Linux 提示 tkinter 相关错误
A: 安装 python3-tk 包

---

## 从源码运行

如果打包版本有问题，可以直接从源码运行：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python linux_do_gui.py
```

---

## GitHub Actions 自动打包（PyInstaller + Nuitka）

仓库已提供 GitHub Actions 工作流，可在提交或打 Tag 时自动打包多平台可执行文件：

- PyInstaller 工作流: `.github/workflows/build-pyinstaller.yml`
- Nuitka 工作流: `.github/workflows/build-nuitka.yml`

### 使用方式

1. 创建并推送版本 Tag（示例）：
   ```bash
   git tag v8.1.0
   git push origin v8.1.0
   ```
2. GitHub Actions 将自动构建并上传对应平台的产物到 Release。
3. 如需手动触发，可在 Actions 页面使用 `workflow_dispatch` 并填写 `version`。

---

## 文件说明

```
linuxdo/
├── linux_do_gui.py           # 主程序
├── build.py                  # 打包脚本
├── README.md                 # 项目说明
├── requirements.txt          # 依赖列表
├── docs/
│   ├── BUILD_GUIDE.md        # 本文档
│   └── Linux 环境安装指南.md  # Linux 环境安装指南
└── dist/
    └── LinuxDoHelper_<...>   # 构建产物示例
```
