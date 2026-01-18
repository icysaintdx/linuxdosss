Linux 环境安装指南

  1. 安装 Python 和 Tkinter

  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3 python3-pip python3-tk

  # CentOS/RHEL
  sudo yum install python3 python3-pip python3-tkinter

  # Arch Linux
  sudo pacman -S python python-pip tk

  2. 安装 Python 依赖

  pip3 install -r requirements.txt

  3. 安装 Chrome 浏览器

  # Ubuntu/Debian
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo dpkg -i google-chrome-stable_current_amd64.deb
  sudo apt-get install -f

  # CentOS/RHEL
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
  sudo yum install ./google-chrome-stable_current_x86_64.rpm

  # Arch Linux
  yay -S google-chrome

  4. 运行程序

  python3 linux_do_gui.py

  ---
  常见问题

  Q: 提示 No module named 'tkinter'
  sudo apt install python3-tk

  Q: 提示 No module named 'DrissionPage'
  pip3 install -r requirements.txt

  Q: 程序启动但浏览器打不开
  确保安装了 Chrome 浏览器：
  google-chrome --version

  Q: 无头服务器（没有图形界面）
  需要安装虚拟显示：
  sudo apt install xvfb
  xvfb-run python3 linux_do_gui.py
