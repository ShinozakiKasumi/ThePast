#!/usr/bin/env python3
"""CI 辅助脚本：在 Ren'Py SDK 自带 Python 下运行 rapt/android.py（如 installsdk）。

用法: ./<sdk>/lib/py3-linux-x86_64/python tools/rapt_run.py <sdk_dir> installsdk
"""
import os
import sys

sdk = os.path.abspath(sys.argv[1])
sys.path.insert(0, sdk)
sys.path.insert(0, os.path.join(sdk, "rapt", "buildlib"))
os.chdir(os.path.join(sdk, "rapt"))
if os.environ.get("BROWSER") is None:
    os.environ["BROWSER"] = "/bin/true"  # 防止 installsdk 打开浏览器
sys.argv = ["android.py"] + sys.argv[2:]
exec(open("android.py", encoding="utf-8").read(), {"__name__": "__main__"})
