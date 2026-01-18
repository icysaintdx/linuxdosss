# -*- coding: utf-8 -*-
"""
Linux.do 论坛刷帖助手 v8.0
功能：
1. 自动获取用户等级和升级进度
2. 多板块浏览
3. 随机点赞帖子和回复
4. 随机回帖
5. 统计报告
6. 防风控机制（随机间隔）
7. 升级进度实时追踪
8. 系统托盘支持
"""

import sys, os, random, time, json, threading
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# 托盘支持
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_SUPPORT = True
except ImportError:
    TRAY_SUPPORT = False

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
except:
    print("pip install DrissionPage")
    sys.exit(1)


def get_icon_path():
    """获取图标路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'icon.ico')


def create_tray_image(color='#0f3460'):
    """创建托盘图标图像"""
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景圆形
    padding = 4
    draw.ellipse([padding, padding, size - padding, size - padding], fill=color)

    # 内圈
    inner_padding = 12
    draw.ellipse([inner_padding, inner_padding, size - inner_padding, size - inner_padding], fill='#1a1a2e')

    # 中心点
    center = size // 2
    dot_size = 8
    draw.ellipse([center - dot_size, center - dot_size, center + dot_size, center + dot_size], fill='#00d9ff')

    return img

# 板块配置
CATS = [
    {"n": "开发调优", "u": "/c/develop/4", "e": True},
    {"n": "国产替代", "u": "/c/domestic/98", "e": True},
    {"n": "资源荟萃", "u": "/c/resource/14", "e": True},
    {"n": "网盘资源", "u": "/c/resource/cloud-asset/94", "e": True},
    {"n": "文档共建", "u": "/c/wiki/42", "e": True},
    {"n": "积分乐园", "u": "/c/credit/106", "e": False},
    {"n": "非我莫属", "u": "/c/job/27", "e": True},
    {"n": "读书成诗", "u": "/c/reading/32", "e": True},
    {"n": "扬帆起航", "u": "/c/startup/46", "e": False},
    {"n": "前沿快讯", "u": "/c/news/34", "e": True},
    {"n": "网络记忆", "u": "/c/feeds/92", "e": True},
    {"n": "福利羊毛", "u": "/c/welfare/36", "e": True},
    {"n": "搞七捻三", "u": "/c/gossip/11", "e": True},
    {"n": "社区孵化", "u": "/c/incubator/102", "e": False},
    {"n": "虫洞广场", "u": "/c/square/110", "e": True},
    {"n": "运营反馈", "u": "/c/feedback/2", "e": False},
]

CFG = {
    "proxy": "127.0.0.1:7897",
    "base": "https://linux.do",
    "connect": "https://connect.linux.do",
    "like_rate": 0.3,
    "reply_rate": 0.05,
    "like_reply_rate": 0.15,
    "scroll_time": 3,
    "wait_min": 1,
    "wait_max": 3,
    "tpl": [
        # 感谢类
        "感谢分享！学习了",
        "感谢楼主的分享",
        "感谢分享，很有帮助",
        "感谢大佬的分享",
        "感谢楼主无私分享",
        "感谢分享，收藏学习",
        "感谢楼主，学到了",
        "感谢分享，受益匪浅",
        # 学习类
        "学习了，谢谢楼主！",
        "学到了新知识，感谢",
        "涨知识了，谢谢分享",
        "学习学习，感谢大佬",
        "又学到了，感谢楼主",
        "学习一下，感谢分享",
        "认真学习中，感谢",
        "好好学习天天向上",
        # 支持类
        "支持一下，感谢分享",
        "支持楼主，继续加油",
        "必须支持，感谢分享",
        "大力支持，感谢楼主",
        "支持支持，学习了",
        "强烈支持，感谢分享",
        # 收藏类
        "好文章，收藏了",
        "收藏了，感谢分享",
        "先收藏，慢慢学习",
        "收藏学习，感谢楼主",
        "马克一下，感谢分享",
        "mark一下，以后学习",
        "先马后看，感谢分享",
        # 赞美类
        "不错不错，学习了",
        "写得很好，感谢分享",
        "内容很棒，感谢楼主",
        "干货满满，感谢分享",
        "质量很高，感谢楼主",
        "很有价值，感谢分享",
        "非常实用，感谢楼主",
        "很有帮助，感谢分享",
        # 前排类
        "前排围观，感谢分享",
        "前排学习，感谢楼主",
        "前排支持，感谢分享",
        "前排关注，学习了",
        "前排占座，感谢分享",
        # 佬类
        "谢谢佬，学习了",
        "感谢佬的分享",
        "佬太强了，学习了",
        "跟着佬学习一下",
        "佬就是佬，感谢分享",
        "大佬牛逼，学习了",
        "膜拜大佬，感谢分享",
        # 其他
        "路过学习，感谢分享",
        "围观学习，感谢楼主",
        "来学习一下，感谢",
        "看看学习，感谢分享",
        "顶一下，感谢分享",
        "顶顶顶，感谢楼主",
        "帮顶一下，感谢分享",
        "好帖必顶，感谢楼主",
        "精华帖子，感谢分享",
        "优质内容，感谢楼主",
        "实用干货，感谢分享",
        "很有意思，感谢楼主",
        "长见识了，感谢分享",
        "开眼界了，感谢楼主",
        "受教了，感谢分享",
        "茅塞顿开，感谢楼主",
    ],
}


class Bot:
    def __init__(s, cfg, cats, lg, update_info=None, update_progress=None):
        s.cfg = cfg
        s.cats = cats
        s.lg = lg
        s.update_info = update_info
        s.update_progress = update_progress  # 新增：更新进度回调
        s.pg = None
        s.run = False
        s.stats = {"topic": 0, "like": 0, "reply": 0, "like_reply": 0}
        s.user_info = None
        s.level_requirements = []  # 保存升级要求

    def _random_delay(s, min_sec=0.5, max_sec=2.0, reason=""):
        """防风控：随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        if reason:
            s.lg(f"[防风控] {reason}，等待 {delay:.1f}s")
        time.sleep(delay)

    def start(s):
        s.lg("启动浏览器...")
        try:
            co = ChromiumOptions()
            if s.cfg["proxy"]:
                co.set_proxy(s.cfg["proxy"])
            co.set_argument("--disable-blink-features=AutomationControlled")
            s.pg = ChromiumPage(co)
            s.lg("浏览器就绪")
            return True
        except Exception as e:
            s.lg("启动失败: " + str(e))
            return False

    def stop(s):
        s.run = False

    def close(s):
        if s.pg:
            try:
                s.pg.quit()
            except:
                pass
            s.pg = None

    def check_login(s, wait_for_login=True, max_wait=600, check_interval=15):
        """
        检查登录状态
        wait_for_login: 是否等待用户登录
        max_wait: 最大等待时间（秒）
        check_interval: 检查间隔（秒）
        """
        s.lg("检查登录...")
        s.pg.get(s.cfg["base"])
        time.sleep(3)

        start_time = time.time()
        check_count = 0
        first_check = True

        while s.run:
            check_count += 1
            try:
                # 不刷新页面，直接检查当前页面的登录状态
                user_ele = s.pg.ele("#current-user", timeout=3)
                if user_ele:
                    try:
                        img = s.pg.ele("#current-user img", timeout=2)
                        s.user_info = {"username": img.attr("title") if img else "用户"}
                    except:
                        s.user_info = {"username": "用户"}
                    s.lg("已登录: " + s.user_info["username"])
                    return True
            except Exception as e:
                pass  # 未找到登录元素，继续等待

            # 未登录
            if not wait_for_login:
                s.lg("未登录，请先登录")
                return False

            # 检查是否超时
            elapsed = time.time() - start_time
            remaining = max_wait - elapsed

            if remaining <= 0:
                s.lg("等待登录超时，请重新启动")
                return False

            if first_check:
                s.lg("未检测到登录，请在浏览器中完成登录")
                s.lg("提示：登录成功后会自动检测，无需其他操作")
                s.lg(f"检查间隔：{check_interval}秒，最长等待：{int(remaining)}秒")
                first_check = False
            else:
                s.lg(f"第{check_count}次检查，未检测到登录，剩余等待{int(remaining)}秒")

            # 等待一段时间后重新检查（不刷新页面，避免打断用户输入）
            time.sleep(check_interval)

        return False

    def get_level_info(s, is_final=False):
        """获取等级信息"""
        s.lg("获取等级信息...")
        try:
            s.pg.get(s.cfg["connect"])
            time.sleep(4)

            info = s.pg.run_js("""
            function getLevelInfo() {
                const result = {
                    username: '',
                    level: '',
                    nextLevel: '',
                    requirements: []
                };
                
                // 获取用户名和等级
                const h1 = document.querySelector('h1');
                if (h1) {
                    const text = h1.textContent;
                    const match = text.match(/\\((.+?)\\)\\s*(\\d+)级用户/);
                    if (match) {
                        result.username = match[1];
                        result.level = match[2];
                    }
                }
                
                // 获取下一级要求
                const h2s = document.querySelectorAll('h2');
                h2s.forEach(h2 => {
                    const text = h2.textContent;
                    if (text.includes('信任级别')) {
                        const match = text.match(/信任级别\\s*(\\d+)/);
                        if (match) {
                            result.nextLevel = match[1];
                        }
                    }
                });
                
                // 获取升级要求表格
                const tables = document.querySelectorAll('table');
                tables.forEach(table => {
                    const rows = table.querySelectorAll('tr');
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 3) {
                            const name = cells[0].textContent.trim();
                            const current = cells[1].textContent.trim();
                            const required = cells[2].textContent.trim();
                            if (name && current && required && name !== '要求') {
                                result.requirements.push({
                                    name: name,
                                    current: current,
                                    required: required
                                });
                            }
                        }
                    });
                });
                
                return result;
            }
            return getLevelInfo();
            """)

            if info:
                s.user_info = info
                s.lg("用户: " + info.get("username", "未知"))
                s.lg("当前等级: " + info.get("level", "未知") + "级")
                if info.get("nextLevel"):
                    s.lg("下一级: " + info.get("nextLevel") + "级")
                if info.get("requirements"):
                    s.lg("升级要求:")
                    for req in info["requirements"][:8]:
                        s.lg(
                            "  "
                            + req["name"]
                            + ": "
                            + req["current"]
                            + "/"
                            + req["required"]
                        )

                # 更新GUI显示
                if s.update_info:
                    s.update_info(info, is_final)

                # 保存升级要求用于进度追踪
                s.level_requirements = info.get("requirements", [])

                return info
        except Exception as e:
            s.lg("获取等级失败: " + str(e))
        return None

    def get_topics(s, cat):
        """使用JS获取帖子列表"""
        url = s.cfg["base"] + cat["u"]
        s.lg("进入板块: " + cat["n"])
        s.pg.get(url)
        s._random_delay(2, 4, "页面加载")

        # 使用JS获取帖子 - 基于实际HTML结构
        topics = s.pg.run_js("""
        function getTopics() {
            const rows = document.querySelectorAll('tr.topic-list-item');
            const topics = [];
            rows.forEach(row => {
                const link = row.querySelector('a.title.raw-link.raw-topic-link');
                if (link) {
                    const href = link.getAttribute('href');
                    const title = link.textContent.trim();
                    const topicId = row.getAttribute('data-topic-id');
                    // 跳过置顶帖
                    if (href && title && !row.classList.contains('pinned')) {
                        topics.push({
                            url: href,
                            title: title.substring(0, 50),
                            id: topicId
                        });
                    }
                }
            });
            return topics;
        }
        return getTopics();
        """)

        return topics or []

    def scroll_page(s, duration=None):
        """滚动页面 - 模拟真实阅读"""
        if duration is None:
            duration = random.uniform(8, 15)  # 增加阅读时间

        s.lg(f"模拟阅读 {duration:.1f}s...")
        start = time.time()
        while time.time() - start < duration and s.run:
            dist = random.randint(150, 400)
            s.pg.run_js(f"window.scrollBy(0, {dist})")
            # 随机停顿，模拟阅读
            time.sleep(random.uniform(1.0, 3.0))

            at_bottom = s.pg.run_js("""
            return (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100;
            """)
            if at_bottom:
                # 到底部后随机停留
                s._random_delay(1, 3, "阅读完毕")
                break

    def do_like(s, index=0):
        """点赞"""
        try:
            result = s.pg.run_js(f"""
            function clickLike(idx) {{
                const buttons = document.querySelectorAll('button.btn-toggle-reaction-like');
                if (buttons.length > idx) {{
                    const btn = buttons[idx];
                    if (!btn.classList.contains('has-like') && !btn.classList.contains('my-likes')) {{
                        btn.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                        setTimeout(() => btn.click(), 300);
                        return true;
                    }}
                }}
                return false;
            }}
            return clickLike({index});
            """)

            if result:
                s._random_delay(0.8, 1.5, "点赞后")
                if index == 0:
                    s.stats["like"] += 1
                    s.lg("点赞主帖成功")
                else:
                    s.stats["like_reply"] += 1
                    s.lg(f"点赞回复 #{index} 成功")
                # 更新进度
                if s.update_progress:
                    s.update_progress(s.stats)
                return True
        except Exception as e:
            s.lg("点赞失败: " + str(e))
        return False

    def do_reply(s, content=None):
        """回帖"""
        try:
            if content is None:
                content = random.choice(s.cfg["tpl"])

            s.lg("准备回复: " + content)

            # 点击回复按钮
            clicked = s.pg.run_js("""
            function clickReply() {
                const btn = document.querySelector('.topic-footer-main-buttons button.create');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            }
            return clickReply();
            """)

            if not clicked:
                s.lg("未找到回复按钮")
                return False

            s._random_delay(1.5, 3, "等待编辑器")

            # 输入内容 - 使用安全的方式传递内容
            safe_content = json.dumps(content)
            s.pg.run_js(f"""
            (function() {{
                const textarea = document.querySelector('#reply-control textarea, .d-editor-input');
                if (textarea) {{
                    textarea.focus();
                    textarea.value = {safe_content};
                    textarea.dispatchEvent(new Event('input', {{bubbles: true}}));
                }}
            }})();
            """)

            s._random_delay(0.8, 1.5, "输入内容后")

            # 提交
            submitted = s.pg.run_js("""
            function submit() {
                const btn = document.querySelector('#reply-control button.create');
                if (btn && !btn.disabled) {
                    btn.click();
                    return true;
                }
                return false;
            }
            return submit();
            """)

            if submitted:
                s._random_delay(2, 4, "回复提交后")
                s.stats["reply"] += 1
                s.lg("回复成功")
                # 更新进度
                if s.update_progress:
                    s.update_progress(s.stats)
                return True
            else:
                s.lg("提交失败")

        except Exception as e:
            s.lg("回复失败: " + str(e))
        return False

    def browse_topic(s, topic):
        """浏览帖子"""
        url = (
            s.cfg["base"] + topic["url"]
            if topic["url"].startswith("/")
            else topic["url"]
        )
        title = topic["title"]

        s.lg("浏览: " + title)
        try:
            s.pg.get(url)
            s._random_delay(2, 4, "帖子加载")
            s.stats["topic"] += 1

            # 更新进度
            if s.update_progress:
                s.update_progress(s.stats)

            # 滚动阅读
            s.scroll_page()
            s._random_delay(1, 2, "阅读后")

            # 获取点赞按钮数量
            btn_count = (
                s.pg.run_js("""
            return document.querySelectorAll('button.btn-toggle-reaction-like').length;
            """)
                or 0
            )

            s.lg(f"找到 {btn_count} 个点赞按钮")

            # 随机点赞主帖
            if btn_count > 0 and random.random() < s.cfg["like_rate"]:
                s.do_like(0)
                s._random_delay(s.cfg["wait_min"], s.cfg["wait_max"], "点赞后休息")

            # 随机点赞回复
            if btn_count > 1:
                for i in range(1, min(btn_count, 5)):
                    if random.random() < s.cfg["like_reply_rate"]:
                        s.do_like(i)
                        s._random_delay(s.cfg["wait_min"], s.cfg["wait_max"], "点赞回复后")

            # 随机回帖
            if random.random() < s.cfg["reply_rate"]:
                s._random_delay(s.cfg["wait_min"], s.cfg["wait_max"], "准备回帖")
                s.do_reply()

            return True
        except Exception as e:
            s.lg("浏览失败: " + str(e))
            return False

    def browse_cat(s, cat):
        """浏览板块"""
        topics = s.get_topics(cat)
        s.lg(f"找到 {len(topics)} 个帖子")

        if not topics:
            return 0

        # 随机选择几个帖子
        count = min(random.randint(3, 8), len(topics))
        selected = random.sample(topics, count)

        browsed = 0
        for topic in selected:
            if not s.run:
                break

            s.browse_topic(topic)
            browsed += 1

            # 防风控：帖子之间随机等待
            if s.run:
                s._random_delay(s.cfg["wait_min"], s.cfg["wait_max"], "切换帖子")

        return browsed

    def run_session(s):
        s.run = True
        s.stats = {"topic": 0, "like": 0, "reply": 0, "like_reply": 0}

        if not s.start():
            return

        login_success = False
        try:
            if not s.check_login(wait_for_login=True, max_wait=300, check_interval=5):
                s.lg("登录检查失败或超时，任务终止")
                return

            login_success = True

            # 获取等级信息
            s.get_level_info()

            # 获取启用的板块
            enabled = [c for c in s.cats if c.get("e", True)]
            random.shuffle(enabled)

            s.lg("=" * 30)
            s.lg(f"开始浏览 {len(enabled)} 个板块")
            s.lg("=" * 30)

            for cat in enabled:
                if not s.run:
                    break
                s.browse_cat(cat)
                # 板块之间随机等待（板块切换用稍长一点的时间）
                s._random_delay(s.cfg["wait_min"] + 1, s.cfg["wait_max"] + 2, "切换板块")

            s.lg("=" * 30)
            s.lg("完成!")
            s.lg(f"浏览帖子: {s.stats['topic']}")
            s.lg(f"点赞主帖: {s.stats['like']}")
            s.lg(f"点赞回复: {s.stats['like_reply']}")
            s.lg(f"回帖数量: {s.stats['reply']}")
            s.lg("=" * 30)

            # 重新获取等级信息以验证效果（在关闭浏览器前）
            if s.pg:
                s.lg("")
                s.lg("=" * 30)
                s.lg("重新获取等级信息验证效果...")
                s.get_level_info(is_final=True)
                s.lg("=" * 30)

        finally:
            s.run = False
            # 只有登录成功后才关闭浏览器，否则保留让用户查看
            if login_success:
                s.close()


class GUI:
    def __init__(s):
        s.rt = tk.Tk()
        s.rt.title("Linux.do 刷帖助手 v8.0")
        s.rt.geometry("750x850")
        s.rt.minsize(750, 750)  # 设置最小窗口大小
        s.rt.configure(bg="#1a1a2e")

        # 设置窗口图标
        try:
            icon_path = get_icon_path()
            if os.path.exists(icon_path):
                s.rt.iconbitmap(icon_path)
        except:
            pass

        # 自定义标题栏
        s.rt.overrideredirect(True)  # 移除默认标题栏

        s.cats = [c.copy() for c in CATS]
        s.cfg = CFG.copy()
        s.bot = None
        s.th = None
        s.req_labels = {}  # 升级要求标签
        s.initial_requirements = []  # 初始升级要求

        # 窗口拖动相关
        s._drag_x = 0
        s._drag_y = 0

        # 托盘相关
        s.tray_icon = None
        s.tray_thread = None
        s._running_status = "就绪"
        s._stop_requested = False

        s._ui()

        # 窗口居中
        s._center_window()

        # 初始化托盘
        if TRAY_SUPPORT:
            s._init_tray()

        # 窗口关闭时的处理
        s.rt.protocol("WM_DELETE_WINDOW", s._on_close_window)

    def _init_tray(s):
        """初始化系统托盘"""
        if not TRAY_SUPPORT:
            return

        def create_menu():
            return pystray.Menu(
                pystray.MenuItem("显示窗口", s._show_window, default=True),
                pystray.MenuItem("开始运行", s._tray_start),
                pystray.MenuItem("停止运行", s._tray_stop),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("退出", s._tray_quit)
            )

        # 创建托盘图标
        s.tray_icon = pystray.Icon(
            "LinuxDoHelper",
            create_tray_image('#0f3460'),
            "Linux.do 刷帖助手 - 就绪",
            create_menu()
        )

        # 在后台线程运行托盘
        s.tray_thread = threading.Thread(target=s.tray_icon.run, daemon=True)
        s.tray_thread.start()

    def _update_tray_status(s, status, stats=None):
        """更新托盘状态"""
        if not TRAY_SUPPORT or not s.tray_icon:
            return

        s._running_status = status

        # 根据状态设置不同颜色
        if status == "运行中":
            color = '#00ff88'  # 绿色
        elif status == "已停止" or status == "已完成":
            color = '#ffaa00'  # 橙色
        else:
            color = '#0f3460'  # 默认蓝色

        # 更新图标
        s.tray_icon.icon = create_tray_image(color)

        # 更新提示文字
        if stats:
            tooltip = f"Linux.do 刷帖助手 - {status}\n"
            tooltip += f"帖子: {stats.get('topic', 0)} | "
            tooltip += f"点赞: {stats.get('like', 0) + stats.get('like_reply', 0)} | "
            tooltip += f"回复: {stats.get('reply', 0)}"
        else:
            tooltip = f"Linux.do 刷帖助手 - {status}"

        s.tray_icon.title = tooltip

    def _show_window(s, icon=None, item=None):
        """显示窗口"""
        s.rt.after(0, s._do_show_window)

    def _do_show_window(s):
        """在主线程中显示窗口"""
        s.rt.deiconify()
        s.rt.overrideredirect(True)
        s.rt.lift()
        s.rt.focus_force()

    def _tray_start(s, icon=None, item=None):
        """从托盘启动"""
        s.rt.after(0, s._start)

    def _tray_stop(s, icon=None, item=None):
        """从托盘停止"""
        s.rt.after(0, s._stop)

    def _tray_quit(s, icon=None, item=None):
        """从托盘退出"""
        if s.tray_icon:
            s.tray_icon.stop()
        s.rt.after(0, s._close)

    def _on_close_window(s):
        """窗口关闭按钮处理 - 最小化到托盘"""
        if TRAY_SUPPORT and s.tray_icon:
            s.rt.withdraw()  # 隐藏窗口
        else:
            s._close()

    def _center_window(s):
        """窗口居中显示"""
        s.rt.update_idletasks()
        w = s.rt.winfo_width()
        h = s.rt.winfo_height()
        sw = s.rt.winfo_screenwidth()
        sh = s.rt.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        s.rt.geometry(f"{w}x{h}+{x}+{y}")

    def _start_drag(s, event):
        """开始拖动窗口"""
        s._drag_x = event.x
        s._drag_y = event.y

    def _do_drag(s, event):
        """拖动窗口"""
        x = s.rt.winfo_x() + event.x - s._drag_x
        y = s.rt.winfo_y() + event.y - s._drag_y
        s.rt.geometry(f"+{x}+{y}")

    def _minimize(s):
        """最小化窗口"""
        if TRAY_SUPPORT and s.tray_icon:
            s.rt.withdraw()  # 最小化到托盘
        else:
            s.rt.overrideredirect(False)
            s.rt.iconify()
            s.rt.bind("<Map>", s._on_restore)

    def _on_restore(s, event):
        """恢复窗口"""
        s.rt.overrideredirect(True)
        s.rt.unbind("<Map>")

    def _close(s):
        """关闭窗口"""
        if s.bot:
            s.bot.stop()
        if s.tray_icon:
            try:
                s.tray_icon.stop()
            except:
                pass
        s.rt.destroy()

    def _ui(s):
        # 自定义标题栏
        title_bar = tk.Frame(s.rt, bg="#0f3460", height=40)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # 标题栏可拖动
        title_bar.bind("<Button-1>", s._start_drag)
        title_bar.bind("<B1-Motion>", s._do_drag)

        # 左侧图标和标题
        title_left = tk.Frame(title_bar, bg="#0f3460")
        title_left.pack(side=tk.LEFT, padx=10)

        tk.Label(
            title_left,
            text="◆",
            font=("Segoe UI", 14),
            bg="#0f3460",
            fg="#00d9ff",
        ).pack(side=tk.LEFT, padx=(5, 8))

        title_label = tk.Label(
            title_left,
            text="Linux.do 刷帖助手 v8.0",
            font=("Microsoft YaHei UI", 11, "bold"),
            bg="#0f3460",
            fg="#ffffff",
        )
        title_label.pack(side=tk.LEFT)
        title_label.bind("<Button-1>", s._start_drag)
        title_label.bind("<B1-Motion>", s._do_drag)

        # 右侧按钮
        btn_frame = tk.Frame(title_bar, bg="#0f3460")
        btn_frame.pack(side=tk.RIGHT, padx=5)

        # 最小化按钮
        min_btn = tk.Label(
            btn_frame,
            text="─",
            font=("Segoe UI", 12),
            bg="#0f3460",
            fg="#ffffff",
            width=4,
            cursor="hand2",
        )
        min_btn.pack(side=tk.LEFT, padx=2)
        min_btn.bind("<Button-1>", lambda e: s._minimize())
        min_btn.bind("<Enter>", lambda e: min_btn.config(bg="#1a5490"))
        min_btn.bind("<Leave>", lambda e: min_btn.config(bg="#0f3460"))

        # 关闭按钮
        close_btn = tk.Label(
            btn_frame,
            text="✕",
            font=("Segoe UI", 12),
            bg="#0f3460",
            fg="#ffffff",
            width=4,
            cursor="hand2",
        )
        close_btn.pack(side=tk.LEFT, padx=2)
        close_btn.bind("<Button-1>", lambda e: s._close())
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#e94560"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#0f3460"))

        # 状态显示
        s.status = tk.StringVar(value="就绪")
        status_label = tk.Label(
            btn_frame,
            textvariable=s.status,
            font=("Microsoft YaHei UI", 9),
            bg="#0f3460",
            fg="#00d9ff",
        )
        status_label.pack(side=tk.LEFT, padx=(0, 15))

        # 内容区域
        content = tk.Frame(s.rt, bg="#1a1a2e")
        content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 用户信息栏
        info_frame = tk.LabelFrame(
            content,
            text=" 用户信息 ",
            bg="#1a1a2e",
            fg="#00d9ff",
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        info_frame.pack(fill=tk.X, padx=15, pady=5)

        info_inner = tk.Frame(info_frame, bg="#1a1a2e")
        info_inner.pack(fill=tk.X, padx=10, pady=5)

        s.user_label = tk.StringVar(value="用户: 未登录")
        s.level_label = tk.StringVar(value="等级: -")
        s.next_level_label = tk.StringVar(value="下一级: -")

        tk.Label(
            info_inner,
            textvariable=s.user_label,
            bg="#1a1a2e",
            fg="#eaeaea",
            font=("Microsoft YaHei UI", 10),
        ).pack(side=tk.LEFT, padx=10)
        tk.Label(
            info_inner,
            textvariable=s.level_label,
            bg="#1a1a2e",
            fg="#00ff88",
            font=("Microsoft YaHei UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10)
        tk.Label(
            info_inner,
            textvariable=s.next_level_label,
            bg="#1a1a2e",
            fg="#ffaa00",
            font=("Microsoft YaHei UI", 10),
        ).pack(side=tk.LEFT, padx=10)

        # 升级进度面板（使用固定高度的Canvas实现滚动）
        progress_frame = tk.LabelFrame(
            content,
            text=" 升级进度追踪 ",
            bg="#1a1a2e",
            fg="#00d9ff",
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        progress_frame.pack(fill=tk.X, padx=15, pady=5)

        # 创建Canvas和滚动条
        s.progress_canvas = tk.Canvas(progress_frame, bg="#1a1a2e", height=200, highlightthickness=0)
        s.progress_scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=s.progress_canvas.yview)
        s.progress_inner = tk.Frame(s.progress_canvas, bg="#1a1a2e")

        s.progress_inner.bind(
            "<Configure>",
            lambda e: s.progress_canvas.configure(scrollregion=s.progress_canvas.bbox("all"))
        )

        s.progress_canvas.create_window((0, 0), window=s.progress_inner, anchor="nw")
        s.progress_canvas.configure(yscrollcommand=s.progress_scrollbar.set)

        s.progress_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        s.progress_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 控制栏
        ctrl = tk.Frame(content, bg="#1a1a2e", pady=5)
        ctrl.pack(fill=tk.X, padx=15)
        tk.Label(ctrl, text="代理:", bg="#1a1a2e", fg="#eaeaea").pack(side=tk.LEFT)
        s.proxy_var = tk.StringVar(value=s.cfg["proxy"])
        tk.Entry(
            ctrl,
            textvariable=s.proxy_var,
            width=18,
            bg="#16213e",
            fg="#eaeaea",
            insertbackground="#eaeaea",
        ).pack(side=tk.LEFT, padx=5)

        s.start_btn = tk.Button(
            ctrl,
            text="开始",
            command=s._start,
            width=10,
            bg="#0f3460",
            fg="white",
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        s.start_btn.pack(side=tk.LEFT, padx=10)
        s.stop_btn = tk.Button(
            ctrl,
            text="停止",
            command=s._stop,
            width=8,
            bg="#e94560",
            fg="white",
            state=tk.DISABLED,
        )
        s.stop_btn.pack(side=tk.LEFT)

        # 主区域
        main = tk.Frame(content, bg="#1a1a2e")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # 左侧 - 板块选择
        left = tk.LabelFrame(
            main,
            text=" 板块选择 ",
            bg="#1a1a2e",
            fg="#00d9ff",
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        s.cat_vars = {}
        for cat in s.cats:
            var = tk.BooleanVar(value=cat.get("e", True))
            s.cat_vars[cat["n"]] = var
            cb = tk.Checkbutton(
                left,
                text=cat["n"],
                variable=var,
                bg="#1a1a2e",
                fg="#eaeaea",
                selectcolor="#0f3460",
                activebackground="#1a1a2e",
                command=lambda n=cat["n"], v=var: s._toggle_cat(n, v),
            )
            cb.pack(anchor=tk.W, pady=1)

        # 右侧
        right = tk.Frame(main, bg="#1a1a2e")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 日志区域
        tk.Label(
            right,
            text="运行日志",
            bg="#1a1a2e",
            fg="#00d9ff",
            font=("Microsoft YaHei UI", 10, "bold"),
        ).pack(anchor=tk.W)
        s.log = scrolledtext.ScrolledText(
            right,
            height=14,
            bg="#16213e",
            fg="#eaeaea",
            font=("Consolas", 9),
            insertbackground="#eaeaea",
        )
        s.log.pack(fill=tk.BOTH, expand=True, pady=5)
        s.log.config(state=tk.DISABLED)

        # 参数设置
        param = tk.Frame(right, bg="#1a1a2e")
        param.pack(fill=tk.X, pady=5)
        tk.Label(param, text="点赞率:", bg="#1a1a2e", fg="#eaeaea").pack(side=tk.LEFT)
        s.like_var = tk.StringVar(value="30")
        tk.Entry(
            param, textvariable=s.like_var, width=4, bg="#16213e", fg="#eaeaea"
        ).pack(side=tk.LEFT)
        tk.Label(param, text="%  回复率:", bg="#1a1a2e", fg="#eaeaea").pack(
            side=tk.LEFT, padx=(10, 0)
        )
        s.reply_var = tk.StringVar(value="5")
        tk.Entry(
            param, textvariable=s.reply_var, width=4, bg="#16213e", fg="#eaeaea"
        ).pack(side=tk.LEFT)
        tk.Label(param, text="%  等待:", bg="#1a1a2e", fg="#eaeaea").pack(
            side=tk.LEFT, padx=(10, 0)
        )
        s.wait_var = tk.StringVar(value="1-3")
        tk.Entry(
            param, textvariable=s.wait_var, width=6, bg="#16213e", fg="#eaeaea"
        ).pack(side=tk.LEFT)
        tk.Label(param, text="秒", bg="#1a1a2e", fg="#eaeaea").pack(side=tk.LEFT)

        # 统计信息
        stats_frame = tk.LabelFrame(
            right,
            text=" 本次统计 ",
            bg="#1a1a2e",
            fg="#00d9ff",
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        stats_frame.pack(fill=tk.X, pady=5)

        stats_inner = tk.Frame(stats_frame, bg="#1a1a2e")
        stats_inner.pack(fill=tk.X, padx=10, pady=5)

        s.stats_topic = tk.StringVar(value="帖子: 0")
        s.stats_like = tk.StringVar(value="点赞: 0")
        s.stats_reply = tk.StringVar(value="回复: 0")

        tk.Label(
            stats_inner,
            textvariable=s.stats_topic,
            bg="#1a1a2e",
            fg="#eaeaea",
            font=("Microsoft YaHei UI", 10),
        ).pack(side=tk.LEFT, padx=15)
        tk.Label(
            stats_inner,
            textvariable=s.stats_like,
            bg="#1a1a2e",
            fg="#eaeaea",
            font=("Microsoft YaHei UI", 10),
        ).pack(side=tk.LEFT, padx=15)
        tk.Label(
            stats_inner,
            textvariable=s.stats_reply,
            bg="#1a1a2e",
            fg="#eaeaea",
            font=("Microsoft YaHei UI", 10),
        ).pack(side=tk.LEFT, padx=15)

    def _toggle_cat(s, name, var):
        for cat in s.cats:
            if cat["n"] == name:
                cat["e"] = var.get()
                break

    def _update_info(s, info, is_final=False):
        """更新用户信息显示"""

        def update():
            if info.get("username"):
                s.user_label.set("用户: " + info["username"])
            if info.get("level"):
                s.level_label.set("等级: " + info["level"] + "级")
            if info.get("nextLevel"):
                s.next_level_label.set("下一级: " + info["nextLevel"] + "级")

            # 更新升级进度面板
            requirements = info.get("requirements", [])
            if requirements:
                if not s.initial_requirements:
                    # 首次获取，保存初始值
                    s.initial_requirements = requirements.copy()
                    s._build_progress_panel(requirements)
                elif is_final:
                    # 结束时更新，显示实际变化
                    s._update_final_progress(requirements)

        s.rt.after(0, update)

    def _update_final_progress(s, new_requirements):
        """结束时更新进度面板，显示实际变化"""
        for new_req in new_requirements:
            name = new_req.get("name", "")
            new_current = new_req.get("current", "0")

            if name in s.req_labels:
                labels = s.req_labels[name]
                try:
                    initial = int(labels["initial"].replace(",", ""))
                    new_val = int(new_current.replace(",", ""))
                    actual_added = new_val - initial

                    labels["current_var"].set(new_current)
                    if actual_added > 0:
                        labels["added_var"].set(f"+{actual_added}")
                    elif actual_added < 0:
                        labels["added_var"].set(str(actual_added))
                    else:
                        labels["added_var"].set("+0")
                except:
                    labels["current_var"].set(new_current)

    def _build_progress_panel(s, requirements):
        """构建升级进度面板"""
        # 清除旧内容
        for widget in s.progress_inner.winfo_children():
            widget.destroy()
        s.req_labels = {}

        # 创建表格头
        headers = ["指标", "初始值", "当前值", "目标值", "本次+"]
        # 列宽设置为0表示自动适应内容宽度
        col_widths = [0, 0, 0, 0, 0]
        # 每列的左右间距 (padx)
        col_padx = [(10, 20), (10, 20), (10, 15), (10, 15), (10, 10)]

        for col, header in enumerate(headers):
            tk.Label(
                s.progress_inner,
                text=header,
                bg="#1a1a2e",
                fg="#00d9ff",
                font=("Microsoft YaHei UI", 9, "bold"),
                anchor="w",
            ).grid(row=0, column=col, padx=col_padx[col], pady=5, sticky="w")

        # 创建数据行
        for row, req in enumerate(requirements[:8], start=1):
            name = req.get("name", "")
            current = req.get("current", "0")
            required = req.get("required", "0")

            # 指标名
            tk.Label(
                s.progress_inner,
                text=name,
                bg="#1a1a2e",
                fg="#eaeaea",
                font=("Microsoft YaHei UI", 9),
                anchor="w",
            ).grid(row=row, column=0, padx=col_padx[0], pady=3, sticky="w")

            # 初始值
            tk.Label(
                s.progress_inner,
                text=current,
                bg="#1a1a2e",
                fg="#888888",
                font=("Microsoft YaHei UI", 9),
                anchor="w",
            ).grid(row=row, column=1, padx=col_padx[1], pady=3, sticky="w")

            # 当前值（可更新）
            current_var = tk.StringVar(value=current)
            tk.Label(
                s.progress_inner,
                textvariable=current_var,
                bg="#1a1a2e",
                fg="#00ff88",
                font=("Microsoft YaHei UI", 9, "bold"),
                anchor="w",
            ).grid(row=row, column=2, padx=col_padx[2], pady=3, sticky="w")

            # 目标值
            tk.Label(
                s.progress_inner,
                text=required,
                bg="#1a1a2e",
                fg="#ffaa00",
                font=("Microsoft YaHei UI", 9),
                anchor="w",
            ).grid(row=row, column=3, padx=col_padx[3], pady=3, sticky="w")

            # 本次增加
            added_var = tk.StringVar(value="+0")
            tk.Label(
                s.progress_inner,
                textvariable=added_var,
                bg="#1a1a2e",
                fg="#00d9ff",
                font=("Microsoft YaHei UI", 9, "bold"),
                anchor="w",
            ).grid(row=row, column=4, padx=col_padx[4], pady=3, sticky="w")

            # 保存引用
            s.req_labels[name] = {
                "initial": current,
                "current_var": current_var,
                "added_var": added_var,
            }

    def _update_progress(s, stats):
        """根据统计更新进度显示"""

        def update():
            if not s.req_labels:
                return

            # 根据统计数据更新相关指标
            for name, labels in s.req_labels.items():
                try:
                    initial = int(labels["initial"].replace(",", ""))
                    added = 0

                    # 根据指标名匹配统计
                    name_lower = name.lower()
                    if "浏览" in name or "阅读" in name or "话题" in name:
                        added = stats.get("topic", 0)
                    elif "点赞" in name or "赞" in name:
                        added = stats.get("like", 0) + stats.get("like_reply", 0)
                    elif "回复" in name or "发帖" in name:
                        added = stats.get("reply", 0)

                    if added > 0:
                        new_val = initial + added
                        labels["current_var"].set(str(new_val))
                        labels["added_var"].set(f"+{added}")
                except:
                    pass

            # 更新托盘状态（实时显示统计）
            s._update_tray_status("运行中", stats)

        s.rt.after(0, update)

    def _lg(s, msg):
        def log():
            ts = datetime.now().strftime("%H:%M:%S")
            s.log.config(state=tk.NORMAL)
            s.log.insert(tk.END, "[" + ts + "] " + msg + "\n")
            s.log.see(tk.END)
            s.log.config(state=tk.DISABLED)

            # 更新统计
            if s.bot:
                s.stats_topic.set(f"帖子: {s.bot.stats['topic']}")
                s.stats_like.set(
                    f"点赞: {s.bot.stats['like'] + s.bot.stats['like_reply']}"
                )
                s.stats_reply.set(f"回复: {s.bot.stats['reply']}")

        s.rt.after(0, log)

    def _start(s):
        if s.th and s.th.is_alive():
            return
        # 更新配置
        s.cfg["proxy"] = s.proxy_var.get()
        try:
            s.cfg["like_rate"] = int(s.like_var.get()) / 100
        except:
            s.cfg["like_rate"] = 0.3
        try:
            s.cfg["reply_rate"] = int(s.reply_var.get()) / 100
        except:
            s.cfg["reply_rate"] = 0.05
        try:
            parts = s.wait_var.get().split("-")
            s.cfg["wait_min"] = float(parts[0])
            s.cfg["wait_max"] = float(parts[1]) if len(parts) > 1 else float(parts[0])
        except:
            s.cfg["wait_min"], s.cfg["wait_max"] = 1, 3

        s.start_btn.config(state=tk.DISABLED)
        s.stop_btn.config(state=tk.NORMAL)
        s.status.set("运行中...")

        # 更新托盘状态
        s._update_tray_status("运行中")

        # 重置初始数据
        s.initial_requirements = []
        s._stop_requested = False

        s.bot = Bot(s.cfg, s.cats, s._lg, s._update_info, s._update_progress)
        s.th = threading.Thread(target=s._run, daemon=True)
        s.th.start()

    def _run(s):
        try:
            s.bot.run_session()
        finally:
            s.rt.after(0, s._done)

    def _done(s):
        s.start_btn.config(state=tk.NORMAL)
        s.stop_btn.config(state=tk.DISABLED)
        if s._stop_requested:
            s.status.set("已停止")
            if s.bot:
                s._update_tray_status("已停止", s.bot.stats)
            else:
                s._update_tray_status("已停止")
        else:
            s.status.set("已完成")
            if s.bot:
                s._update_tray_status("已完成", s.bot.stats)
            else:
                s._update_tray_status("已完成")
        s._stop_requested = False

    def _stop(s):
        if s.bot:
            s.bot.stop()
        s._stop_requested = True
        s.status.set("正在停止...")
        s._update_tray_status("已停止")

    def run(s):
        s.rt.mainloop()


if __name__ == "__main__":
    GUI().run()
