# DESIGN.md — 《过去 // The Past》设计文档

> Ren'Py 8 心理恐怖 VN，线框档案风。
> 本文档记录局内界面（in-game UI）系统化设置与 fx 系统。

## 目录

- [1. 全局规则](#1-全局规则)
- [2. 调色板与令牌](#2-调色板与令牌)
- [3. 布局规格](#3-布局规格)
- [4. 组件规格](#4-组件规格)
- [5. 选择菜单](#5-选择菜单)
- [6. confirm 与系统屏幕](#6-confirm-与系统屏幕)
- [7. fx 系统（9 旗标）](#7-fx-系统9-旗标)
- [8. 自查清单](#8-自查清单)

---

## 1. 全局规则

- 两窗之外纯黑 Solid；棋盘格透明纹理严禁出现。
- 颜色全走 tokens（`design_tokens.rpy`），PALETTE 一键切换，不硬编码。
- 局内默认 palette B（深 `#05070a` / 浅 `#a8c0e8` / 强调红 `#c1272d` / 框线 `#cfcfcf`）。
- 字体：中文 Sarasa UI TC（更紗黑體 UI TC）；拉丁 IBM Plex Mono（FontGroup 自动回退）。
- 所有文字由引擎字体渲染；美术图内不得出现可读文字。
- 全屏粒子层：约 25 个白色 1-2px 点，alpha 0.3-0.8，缓慢下坠漂移，覆盖整屏（含两窗外黑边），默认开，设置可关（`persistent.particles`）。

## 2. 调色板与令牌

`game/design_tokens.rpy` 为单一可改源。`define PALETTE = "B"` 切换。

| 令牌 | Palette A | Palette B | 用途 |
|------|-----------|-----------|------|
| `COL_BG` | `#0a0a0a` | `#05070a` | 底色 |
| `COL_PAPER` | `#e6e0cf` | `#a8c0e8` | 浅色元素（名字栏文字等） |
| `COL_ACCENT` | `#c1272d` | `#c1272d` | 强调红（推进指示/选择 hover/fx） |
| `COL_FRAME` | `#e6e0cf` | `#cfcfcf` | 1px 框线 |
| `COL_TEXT` | `#e6e0cf` | `#e6e6e6` | 正文 |
| `COL_GRAY` | `#6b6b6b` | `#5a6b8a` | idle/内心 |
| `COL_INNER` | = COL_GRAY | `#5a6b8a` | who=null 内心独白 |
| `COL_QM_GRAY` | `#6b6b6b` | `#9a9a9a` | 快捷菜单 idle |
| `COL_QM_INSENS` | `#6b6b6b60` | `#555555` | 快捷菜单不可用 |
| `COL_QM_HOVER` | `#e6e0cf` | `#e6e6e6` | 快捷菜单 hover |

## 3. 布局规格

基准 1280×720，数值进 tokens 可调。

| 组件 | 令牌 | 像素值 | 规格 |
|------|------|--------|------|
| 图像窗 | `IMG_WIN_X/Y/W/H` | 154, 80, 972, 410 | 左右边距各 12% 宽；上边距 11% 高；高 57%；1px 边框 |
| 文本窗 | `TXT_WIN_X/Y/W/H` | 154, 511, 972, 202 | 左右边距同图像窗；上缘 71% 高；下缘距屏底 1%；1px 边框；内纯黑 |
| 接缝 | `SEAM_Y` | 500.5 | 图像窗底(490)与文本窗顶(511)的中点 |
| 正文起始 | `TEXT_START_X/Y` | 269, 568 | x = 21% 屏宽；y = 文本窗顶 + 8% 屏高 |

## 4. 组件规格

### 名字栏（who != null）
- 黑底 + 1px 边框 `#cfcfcf`；左缘 x ≈ 14%（`NAMEBOX_X = 179`）。
- 高约 8% 屏高（`NAMEBOX_H = 58`）；竖向中心 = 骑缝（`NAMEBOX_Y = 471.5`）。
- 宽随文字自适应（默认 `NAMEBOX_W = 200`，token 可调）。
- 文本 `"[NAME]"` 等宽浅色（`COL_PAPER`）居中，含方括号。
- 骑缝：上半压图像窗下沿、下半压文本窗上沿。

### 脸部框（who != null）
- 右侧方形说话人特写；右边距约 3%（`FACEBOX_X = 1037`）。
- 宽约 16% 屏宽，近正方形（`FACEBOX_W = FACEBOX_H = 205`）。
- 上缘约 68% 高（`FACEBOX_Y = 490`），骑文本窗上沿，伸入两窗黑缝。
- 双层框：外 1px `#cfcfcf`，4px 黑缝（`FACEBOX_GAP = 4`），内 1px `#cfcfcf`。
- 内显示说话人脸图，全彩。

### 立绘（有角色时）
- 全彩、不抖动、1-2px 亮描边；水平居中（`SPRITE_X = 400`）。
- 底边伸入图像窗底框下方约 2.5% 屏高的黑缝（`SPRITE_BREAK = 18`），不裁切。
- z-order：图像窗之上、名字栏/脸部框之下。

### 推进指示
- displayable 绘制红色小三角（6 条 Solid 横带堆叠成三角）。
- 出现于文本窗内右下（`ADV_IND_X/Y`），`blink` transform 闪烁。

### 正文
- 左对齐，等宽 `COL_TEXT`（`#e6e6e6`），约 22px，行高 1.6（`line_leading = 13`），打字机。
- who=null 时切内心样式：`COL_INNER`（`#9a9a9a`），约 20px；隐藏名字栏/脸部框/立绘。

### 快捷菜单
- 文本窗内部底端（距窗底框约 10px），水平居中一行。
- 条目：`回退 記錄 略過 自動 存檔 快儲 快讀 設定`（繁体中文；英文界面显示 BACK LOG SKIP AUTO SAVE Q.SAVE Q.LOAD SETTINGS）。
- 等宽约 14px、字距 2、灰 `#9a9a9a`；不可用 `#555555`；hover `#e6e6e6`；条目间距约 3 字宽。

## 5. 选择菜单

- 1px 浅色描边（`COL_FRAME`）透明底按钮，居中纵列等宽留距。
- hover 反红底（`COL_ACCENT`）浅色字；`choice_in` transform 0.1s 抖动入场。

## 6. confirm 与系统屏幕

- confirm：全屏墨黑半透遮罩（`COL_BG + "C0"`）+ 居中线框小框，中文等宽提示。
- 确定/返回线框按钮（1px `COL_FRAME`，hover 红底）。
- yesno 类屏幕全部本地化（`options.rpy` 覆盖 `layout.*` 字符串）。
- load/save/preferences 保留默认结构，仅用 gui 变量覆盖颜色/字体。

## 7. fx 系统（9 旗标）

fx 为 ATL transform / 屏幕覆盖层，可由 `scene`/`show` 的 `at` 子句或 `fx_trigger()` 触发。
JSON 解释器（已接线，逻辑不改）将 JSON 节点 `fx` 数组映射到这些效果。

### scene/show 型（直接用 `at` 子句）

| 旗标 | 说明 | 用法示例 | JSON 示例 |
|------|------|----------|-----------|
| `invert` | 反相颜色（RGB 255-x） | `scene bg snow_path at fx_invert` | `{"fx":["invert"],"fx_dur":0.4}` |
| `shake` | 屏幕抖动（x/y 随机偏移衰减） | `scene bg snow_path at fx_shake` | `{"fx":["shake"],"fx_dur":0.3}` |
| `glitch` | RGB 通道分离 + 横向切片错位 | `scene bg snow_path at fx_glitch` | `{"fx":["glitch"],"fx_dur":0.25}` |
| `sprite_dither` | 立绘切双色抖动模式（灰度+高对比） | `show sprite_snow at fx_sprite_dither` | `{"fx":["sprite_dither"]}` |

### 全屏覆盖型（由 `fx_trigger()` 或 `renpy.show_screen` 调用）

| 旗标 | 说明 | 用法示例 | JSON 示例 |
|------|------|----------|-----------|
| `flash` | 全屏白闪一帧后淡出 | `$ fx_trigger("flash", 0.2)` | `{"fx":["flash"],"fx_dur":0.2}` |
| `radio` | 强无线电噪点叠加（高频颗粒） | `$ fx_trigger("radio", 1.0)` | `{"fx":["radio"],"fx_dur":1.0}` |
| `radio_whisper` | 弱无线电噪点（低 alpha 颗粒） | `$ fx_trigger("radio_whisper", 2.0)` | `{"fx":["radio_whisper"],"fx_dur":2.0}` |
| `color_return` | 从当前 fx 状态平滑回正正常色 | `$ fx_trigger("color_return", 0.5)` | `{"fx":["color_return"],"fx_dur":0.5}` |

### 控制型

| 旗标 | 说明 | JSON 示例 |
|------|------|-----------|
| `repeat` | 当前节点重复播放指定次数 | `{"fx":["repeat"],"repeat":3}` |

### 实现位置
- ATL transforms：`game/screens.rpy` 顶部 `fx_*` transform 块。
- 覆盖屏幕：`game/screens.rpy` `screen fx_flash` / `fx_radio` / `fx_radio_whisper` / `fx_color_return`。
- 调度函数：`game/screens.rpy` init python 中 `fx_trigger(name, dur)`。

## 8. 自查清单

三种情况自玩覆盖：

| 情况 | 组件 | 预期 |
|------|------|------|
| 旁白(who=null) | 名字栏/脸部框/立绘 | 隐藏 |
| 旁白(who=null) | 正文 | `#9a9a9a`，约 20px |
| 具名(who!=null) | 名字栏 | 骑缝，黑底+1px框，"[NAME]" 浅色居中 |
| 具名(who!=null) | 脸部框 | 右侧双层框，骑文本窗上沿，伸入黑缝 |
| 具名(who!=null) | 立绘 | 居中，底边破框伸入黑缝 18px，不裁切 |
| 具名(who!=null) | 正文 | `#e6e6e6`，约 22px，行高 1.6 |
| 选择 | choice 按钮 | 1px 浅色描边透明底，hover 红底浅字，0.1s 抖动入场 |
| 通用 | 推进三角 | 文本窗内右下，红色，闪烁 |
| 通用 | 快捷菜单 | 文本窗内底端，繁体中文，#9a9a9a/#555555/#e6e6e6 |
| 通用 | 粒子层 | 全屏 25 白点，覆盖黑边，可关 |
| 通用 | 两窗外 | 纯黑 Solid，无棋盘格 |
