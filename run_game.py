#!/usr/bin/env python3
"""ThePast — 使用 Ren'Py 8 SDK 启动游戏。

用法:
    python3 run_game.py             # 启动游戏
    python3 run_game.py lint        # 运行 lint 检查

SDK 路径可用环境变量 RENPY_SDK 覆盖。
"""
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_SDK = Path.home() / "renpy-8.5.3-sdk"


def main() -> int:
    sdk = Path(os.environ.get("RENPY_SDK", DEFAULT_SDK))
    launcher = sdk / "renpy.sh"
    if not launcher.is_file():
        print(
            f"錯誤：找不到 Ren'Py SDK（{sdk}）。"
            "請設定 RENPY_SDK 環境變數指向 SDK 目錄。",
            file=sys.stderr,
        )
        return 1
    return subprocess.call([str(launcher), str(PROJECT_DIR), *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())
