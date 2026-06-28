# -*- coding: utf-8 -*-
"""打包前自测：配置持久化 + AIClient 逻辑（不启动 GUI / 浏览器）"""

import importlib.util
import json
import os
import sys
import types


def _stub_heavy_imports():
    for name in [
        "tkinter",
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.messagebox",
        "DrissionPage",
        "pystray",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
    ]:
        sys.modules[name] = types.ModuleType(name)
    sys.modules["tkinter"].Tk = object
    sys.modules["tkinter"].ttk = sys.modules["tkinter.ttk"]
    sys.modules["DrissionPage"].ChromiumPage = object
    sys.modules["DrissionPage"].ChromiumOptions = object


def load_module():
    _stub_heavy_imports()
    path = os.path.join(os.path.dirname(__file__), "linux_do_gui.py")
    spec = importlib.util.spec_from_file_location("linux_do_gui", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_config_roundtrip(mod):
    cfg_path = mod._config_path()
    backup = None
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            backup = f.read()

    try:
        test_cfg = dict(mod.CFG)
        test_cfg.update(
            ai_enabled=True,
            ai_key="sk-test-only",
            ai_url="https://example.com/v1",
            ai_model="claude-opus-4-8",
            proxy="127.0.0.1:7897",
        )
        mod.save_config(test_cfg)
        with open(cfg_path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["ai_enabled"] is True
        assert saved["ai_key"] == "sk-test-only"
        assert saved["ai_url"] == "https://example.com/v1"

        mod.CFG["ai_enabled"] = False
        mod.CFG["ai_key"] = ""
        mod.load_config()
        assert mod.CFG["ai_enabled"] is True
        assert mod.CFG["ai_key"] == "sk-test-only"
        assert mod.resolve_ai_system_prompt(mod.CFG) == mod.DEFAULT_AI_SYSTEM_PROMPT
        mod.CFG["ai_use_custom_prompt"] = True
        mod.CFG["ai_system_prompt"] = "我的自定义系统提示"
        assert mod.resolve_ai_system_prompt(mod.CFG) == "我的自定义系统提示"
        print("[OK] config save/load")
    finally:
        if backup is None:
            if os.path.exists(cfg_path):
                os.remove(cfg_path)
        else:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(backup)


def test_ai_client(mod):
    class FakeBlock:
        def __init__(self, t):
            self.type = "text"
            self.text = t

    class FakeResp:
        stop_reason = "end_turn"
        content = [FakeBlock("这帖子讲得很实在，我照着试了一下确实有用，谢啦")]

    ai = mod.AIClient("https://x", "k", "claude-opus-4-8", lg=lambda *a, **k: None)
    assert "普通老用户" in ai.system_prompt or "L站" in ai.system_prompt
    ai2 = mod.AIClient(
        "https://x",
        "k",
        "claude-opus-4-8",
        system_prompt="自定义提示词测试不少于十六个字的要求",
    )
    assert ai2.system_prompt.startswith("自定义")
    print("[OK] custom/default system prompt")
    ai._client = types.SimpleNamespace(
        messages=types.SimpleNamespace(create=lambda **kw: FakeResp())
    )
    text = ai.generate_reply("测试标题", ["主帖内容", "一楼回复"])
    assert text and len(text) >= 16, text
    print("[OK] generate_reply:", text)

    class RefuseResp:
        stop_reason = "refusal"
        content = []

    ai._client = types.SimpleNamespace(
        messages=types.SimpleNamespace(create=lambda **kw: RefuseResp())
    )
    assert ai.generate_reply("t", ["x"]) is None
    print("[OK] refusal -> skip")

    def boom(**kw):
        raise RuntimeError("network error")

    ai._client = types.SimpleNamespace(
        messages=types.SimpleNamespace(create=lambda **kw: boom())
    )
    assert ai.generate_reply("t", ["x"]) is None
    print("[OK] exception -> skip")


def test_anthropic_import():
    import anthropic

    c = anthropic.Anthropic(api_key="sk-test", base_url="https://example.com")
    assert "example.com" in str(c.base_url)
    print("[OK] anthropic SDK import, version", anthropic.__version__)


def main():
    print("=" * 50)
    print("Linux.do 助手 — 打包前测试")
    print("=" * 50)
    test_anthropic_import()
    mod = load_module()
    test_config_roundtrip(mod)
    test_ai_client(mod)
    print("=" * 50)
    print("全部通过，可以打包 exe")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())