# -*- coding: utf-8 -*-
"""
Linux.do 刷帖助手 - 多平台打包脚本
支持 Windows、macOS、Linux
"""

import os
import sys
import subprocess
import shutil
import platform

# 项目信息
APP_NAME = "LinuxDoHelper"
APP_VERSION = "8.0"
MAIN_SCRIPT = "linux_do_gui.py"
ICON_WIN = "icon.ico"  # Windows图标
ICON_MAC = "icon.icns"  # macOS图标

def get_platform():
    """获取当前平台"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return system

def clean_build():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"已清理: {d}")

    # 清理 .spec 文件
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)
            print(f"已清理: {f}")

def build_windows():
    """打包 Windows exe"""
    print("\n" + "=" * 50)
    print("开始打包 Windows 版本...")
    print("=" * 50)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", f"{APP_NAME}_v{APP_VERSION}_Windows",
        "--add-data", f"{MAIN_SCRIPT};.",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.scrolledtext",
        "--hidden-import", "DrissionPage",
        "--hidden-import", "pystray",
        "--hidden-import", "PIL",
        "--clean",
        "--noconfirm",
        MAIN_SCRIPT
    ]

    # 打包图标数据，供运行时托盘与窗口图标使用
    if os.path.exists(ICON_WIN):
        cmd.extend(["--add-data", f"{ICON_WIN};."])

    # 如果有图标文件
    if os.path.exists(ICON_WIN):
        cmd.extend(["--icon", ICON_WIN])

    try:
        subprocess.run(cmd, check=True)
        print(f"\nWindows 版本打包成功!")
        print(f"输出文件: dist/{APP_NAME}_v{APP_VERSION}_Windows.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False

def build_macos():
    """打包 macOS app"""
    print("\n" + "=" * 50)
    print("开始打包 macOS 版本...")
    print("=" * 50)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", f"{APP_NAME}_v{APP_VERSION}_macOS",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.scrolledtext",
        "--hidden-import", "DrissionPage",
        "--hidden-import", "pystray",
        "--hidden-import", "PIL",
        "--clean",
        "--noconfirm",
        MAIN_SCRIPT
    ]

    # 打包图标数据，供运行时托盘与窗口图标使用
    if os.path.exists(ICON_WIN):
        cmd.extend(["--add-data", f"{ICON_WIN}:."])

    # 如果有图标文件
    if os.path.exists(ICON_MAC):
        cmd.extend(["--icon", ICON_MAC])

    try:
        subprocess.run(cmd, check=True)
        print(f"\nmacOS 版本打包成功!")
        print(f"输出文件: dist/{APP_NAME}_v{APP_VERSION}_macOS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False

def build_linux():
    """打包 Linux 版本"""
    print("\n" + "=" * 50)
    print("开始打包 Linux 版本...")
    print("=" * 50)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", f"{APP_NAME}_v{APP_VERSION}_Linux",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.scrolledtext",
        "--hidden-import", "DrissionPage",
        "--hidden-import", "pystray",
        "--hidden-import", "PIL",
        "--clean",
        "--noconfirm",
        MAIN_SCRIPT
    ]

    # 打包图标数据，供运行时托盘与窗口图标使用
    if os.path.exists(ICON_WIN):
        cmd.extend(["--add-data", f"{ICON_WIN}:."])

    try:
        subprocess.run(cmd, check=True)
        print(f"\nLinux 版本打包成功!")
        print(f"输出文件: dist/{APP_NAME}_v{APP_VERSION}_Linux")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print(f"Linux.do 刷帖助手 v{APP_VERSION} 打包工具")
    print("=" * 50)

    current_platform = get_platform()
    print(f"当前平台: {current_platform}")

    # 检查主脚本是否存在
    if not os.path.exists(MAIN_SCRIPT):
        print(f"错误: 找不到主脚本 {MAIN_SCRIPT}")
        sys.exit(1)

    # 清理旧的构建文件
    clean_build()

    # 根据当前平台打包
    if current_platform == "windows":
        success = build_windows()
    elif current_platform == "macos":
        success = build_macos()
    elif current_platform == "linux":
        success = build_linux()
    else:
        print(f"不支持的平台: {current_platform}")
        sys.exit(1)

    if success:
        print("\n" + "=" * 50)
        print("打包完成!")
        print("=" * 50)
        print("\n注意事项:")
        print("1. 运行程序需要安装 Chrome 浏览器")
        print("2. 首次运行可能需要允许防火墙访问")
        print("3. macOS/Linux 用户可能需要赋予执行权限: chmod +x <文件名>")
    else:
        print("\n打包失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
