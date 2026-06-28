# -*- coding: utf-8 -*-
"""冒烟测试：启动浏览器并尝试打开 linux.do（不启动 GUI）"""
import importlib.util, os, sys, time

def load_module():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__ if '__file__' in dir() else '.')), 'linux_do_gui.py')
    path = os.path.join(os.getcwd(), 'linux_do_gui.py')
    spec = importlib.util.spec_from_file_location('linux_do_gui', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    print('=' * 50)
    print('浏览器冒烟测试 — 打开 https://linux.do')
    print('=' * 50)
    mod = load_module()
    mod.load_config()
    cfg = mod.CFG.copy()
    proxy = mod.normalize_proxy(cfg.get('proxy'))
    print('代理:', proxy or '(直连)')
    print('数据目录:', mod._app_dir())
    from DrissionPage import ChromiumPage, ChromiumOptions
    co = ChromiumOptions()
    co.set_user_data_path(os.path.join(mod._app_dir(), 'browser_data'))
    if proxy:
        co.set_proxy(proxy)
    co.set_argument('--disable-blink-features=AutomationControlled')
    print('启动 Chrome...')
    page = ChromiumPage(co)
    url = cfg['base']
    print('访问:', url)
    ok = page.get(url, show_errmsg=True, retry=2, timeout=90)
    time.sleep(2)
    current = page.url
    title = page.title
    print('get() 返回:', ok)
    print('当前 URL:', current)
    print('页面标题:', title)
    if ok and 'linux.do' in (current or ''):
        print('[OK] 页面已打开')
        code = 0
    else:
        print('[FAIL] 未能正常打开 linux.do')
        code = 1
    try:
        page.quit()
    except Exception:
        pass
    print('=' * 50)
    return code

if __name__ == '__main__':
    sys.exit(main())
