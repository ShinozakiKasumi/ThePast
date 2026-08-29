#!/usr/bin/env bash
# ThePast — 使用 Ren'Py 8 SDK 启动游戏。
#
# 用法:
#   ./run_game.sh            # 启动游戏
#   ./run_game.sh lint       # 运行 lint 检查
#
# SDK 路径可用环境变量 RENPY_SDK 覆盖，例如:
#   RENPY_SDK=/path/to/renpy-8.5.3-sdk ./run_game.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENPY_SDK="${RENPY_SDK:-$HOME/renpy-8.5.3-sdk}"
LAUNCHER="$RENPY_SDK/renpy.sh"

if [[ ! -f "$LAUNCHER" ]]; then
    echo "錯誤：找不到 Ren'Py SDK（$RENPY_SDK）。" >&2
    echo "請設定 RENPY_SDK 環境變數指向 SDK 目錄。" >&2
    exit 1
fi

exec "$LAUNCHER" "$PROJECT_DIR" "$@"
