---
feature: vn-main-menu
status: designed
updated: 2026-08-06
branch: main
commits: 
---

# VN 主界面脚手架（线框档案风）

## Report

## [S1] Problem
在空目录初始化一个 Ren'Py 8 视觉小说项目，本阶段只构建"主界面"层：
标题/主菜单 + 局内布局 + 选择/快捷菜单。不写实际剧情，仅占位测试句。
视觉风格为线框档案风：
纯黑底、1px 线框细边、双色调抖动(1-bit)图像、等宽/打字机字体、字距菜单——"档案/终端"感。

## [S2] Design

### 设计 tokens（集中一处可改：`game/design_tokens.rpy`）
- `define PALETTE = "A"` 单个变量切换两套调色板。
- 调色板A（默认，中式）：墨黑 `#0a0a0a` / 纸色 `#e6e0cf` / 红笔红 `#c1272d` / 灰 `#6b6b6b`；
  抖动双色 = 墨黑+纸色；强调色 = 红。
- 调色板B（暗色主调）：深 `#05070a` / 浅 `#a8c0e8`；强调色 = 浅色。
- 框线 1px = 框线色（A=纸色，B=浅色）。
- 字体：中文 `NotoSansMonoCJKsc-Regular.otf`（Bold 备用）；拉丁 `IBMPlexMono-Regular.ttf`。
- 布局比例：图像窗约占 60% 高（带框），文本窗约占 30% 高（带框），中间黑留白，
  底部一行字距小字快捷菜单。全局纯黑底。

### 占位背景生成（`tools/gen_placeholders.py`，开发工具，运行时不依赖）
- PIL 生成 1280×720 双色 Bayer 4x4 抖动占位背景（抽象渐变+噪点，暗示走廊/教室/校门夜景），
  存入 `game/assets/bg/`。双色取自当前调色板；参数化 palette/分辨率/seed。
- 预留 `--input` 目录接口：真实照片 → 灰度→对比→降采样→Bayer→双色映射→噪点。

### 标题/主菜单（`screens.rpy: main_menu`）
- 标题《　》等宽逐字出现，最后一字延迟半拍。
- 角落黄历风味块（占位）：纸底红字"宜：开始　忌：回头"，小尺寸。
- 菜单：开始游戏/继续/读取/设置/退出；idle 灰，hover 强调色 + 1帧 RGB 分离 + 1px 位移；
  无存档时"继续"禁用置灰。
- 底部版本/版权占位等宽小字；音频钩子函数占位。

### 局内布局（`screens.rpy: say` + `game_menu`）
- 图像窗：1px 框，显示抖动背景。
- 文本窗：1px 框纯黑底；正文纸色等宽打字机；推进指示闪烁红色"▼"。
- 无独立名字栏：角色名以红色等宽小字"名字："内联句首；who=null 切内心样式（灰色、更小）。
- 选择菜单：1px 纸色描边透明底；hover 反红底纸色字；0.1s 抖动入场。
- 快捷菜单一行：回看/日志/跳过/自动/保存/快存/快读/设置；等宽字距灰，hover 强调色。

### 其余屏幕
- load/save/preferences 保留默认结构，仅用 gui 变量覆盖颜色/字体。

### 微氛围
- 图像窗低频偶发 1 帧抖动噪点闪烁，默认开启（ATL transform 实现）。

### 测试内容（`script.rpy: label start`）
- 3 句占位（含 1 句 who=null、1 个两选项 choice），如"【占位台词01】"，结束回标题。

## [S3] Out of Scope
- 剧情 JSON 解释器：不实现，留 TODO（README 记录）。
- 走路系统：不实现，留 TODO（README 记录）。
- 真实美术资产、音乐音效、存档图标定制：本阶段不做。
- 调色板B 的完整视觉调校：作为"试味"提供，本阶段不做像素级细调。

## Tasks
- [ ] T1: 设计 tokens 文件 `game/design_tokens.rpy` — acceptance: `PALETTE` 切换 A/B 时所有颜色 define 跟随变化，lint 通过 (covers: S2)
- [ ] T2: 占位生成脚本 `tools/gen_placeholders.py` — acceptance: 参数化 palette/分辨率/seed，Bayer 4x4 双色抖动，`--input` 接口可用 (covers: S2)
- [ ] T3: 生成占位背景到 `game/assets/bg/` — acceptance: 至少 3 张 1280×720 PNG，lint 能加载 (depends: T1,T2; covers: S2)
- [ ] T4: 项目配置 `options.rpy` — acceptance: 游戏名/版本/窗口配置正确，lint 通过 (covers: S2)
- [ ] T5: GUI 覆盖 `gui.rpy` — acceptance: 颜色/字体经 gui 变量覆盖两套调色板 (depends: T1; covers: S2)
- [ ] T6: 主菜单 `main_menu` screen — acceptance: 标题逐字、黄历块、菜单 hover 效果、无存档置灰、版本底栏 (depends: T1; covers: S2)
- [ ] T7: 局内布局 say + 图像窗 + 文本窗 — acceptance: 1px 框、内联名字、who=null 内心样式、▼ 闪烁推进指示 (depends: T1,T5; covers: S2)
- [ ] T8: choice + quick_menu screens — acceptance: choice 1px 描边 hover 反色 0.1s 入场；quick_menu 一行 8 项 hover 强调色 (depends: T1; covers: S2)
- [ ] T9: load/save/preferences 默认结构 + gui 覆盖 — acceptance: 三屏可打开，颜色字体跟随调色板 (depends: T5; covers: S2)
- [ ] T10: 测试内容 `script.rpy` label start — acceptance: 3 句占位含 who=null 与两选项 choice，结束回标题 (depends: T7,T8; covers: S2)
- [ ] T11: README + git init + lint 验证 — acceptance: README 含运行/切调色板/gen_placeholders/下阶段 TODO；lint 通过或说明 (depends: T1-T10; covers: S2)
