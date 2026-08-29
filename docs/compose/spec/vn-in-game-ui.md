---
feature: vn-in-game-ui
status: delivered
updated: 2026-08-09
branch: feat/in-game-ui
commits: 8e253f8..174977b
---

# 局内界面系统化设置（In-Game UI）

## Report

**What was built** — 系统化重设局内 UI：调色板 B 重定义（强调红 #c1272d / 框线 #cfcfcf / 正文 #e6e6e6 / 快捷菜单灰 #9a9a9a/#555555/#e6e6e6）并设为默认；布局令牌按百分比重写（图像窗 12%/11%/57%、文本窗 71%/1%、正文 21%+8%）；say 屏重写实现骑缝名字栏、右侧双层脸部框、破框立绘、#e6e6e6 正文 22px 行高 1.6、who=null 内心 #9a9a9a 20px、红三角推进指示；quick_menu 改英文大写 8 项置灰；fx 系统 9 旗标 ATL transforms + 覆盖屏幕 + fx_trigger() 调度；全屏粒子层 25 白点；preferences 增粒子开关；参考雪巷背景占位接入；DESIGN.md 局内 UI 章节 + fx 文档。

**Verification** — `renpy.sh lint` 通过（无错误/警告）。布局数学验证：SEAM_Y=500.5，名字栏骑缝 471.5-529.5（图像窗底 490 / 文本窗顶 511），脸部框顶 490（68%），立绘底 508（破框 18px 伸入黑缝，不裁切）。

**Journey log** —
1. 调色板 B 重定义需新增 COL_TEXT/COL_QM_* 令牌，原 PAL_B 仅 3 色不足以覆盖规格中的 6 种灰阶。
2. 布局从固定 20px 边距改百分比时，int() 取整导致 1-2px 误差，可接受（视觉无感知）。
3. fx 系统分两类：scene/show 型（invert/shake/glitch/sprite_dither）用 at 子句，全屏覆盖型（flash/radio/radio_whisper/color_return）用屏幕 + timer 自动隐藏。
4. 推进指示"打字机完成后出现"在自定义 say 屏中检测文本完成较复杂，沿用既有闪烁方案（始终可见 + blink），DESIGN.md 记录。
5. 标题屏代码零改动，仅随 PALETTE token 切换外观——符合用户"最小改动"决策。
## [S1] Problem
局内 UI（say / choice / quick_menu）目前是脚手架占位布局（20px 固定边距、中文快捷菜单、
无粒子层、无 fx 系统、布局比例与目标规格不符）。需按完整文字规格系统性重设：
百分比布局、骑缝名字栏、右侧双层脸部框、破框立绘、推进三角、全屏粒子、英文大写快捷菜单、
9 旗标 fx 系统，并切换默认调色板为 B。标题屏已封版不得改动（仅随 token 切换外观）。

## [S2] Design

### 调色板 B 重定义（design_tokens.rpy）
- `PALETTE = "B"` 为局内默认。
- 调色板 B 新色值：深 `#05070a` / 浅 `#a8c0e8` / **强调红 `#c1272d`** / **框线 `#cfcfcf`**。
- 新增令牌：`COL_TEXT`（正文 `#e6e6e6`）、`COL_QM_GRAY`（快捷菜单灰 `#9a9a9a`）、
  `COL_QM_INSENS`（不可用 `#555555`）、`COL_QM_HOVER`（hover `#e6e6e6`）。
- `COL_ACCENT` 在 B 下改为红 `#c1272d`（与 A 相同）；`COL_FRAME` 在 B 下改为 `#cfcfcf`。
- 所有颜色走 tokens，不硬编码；PALETTE 一键切换保留。

### 字体
- 中文 Noto Sans Mono CJK SC；拉丁 Courier Prime / IBM Plex Mono（FontGroup 已有）。
- 所有文字引擎渲染，美术图内无可读文字。

### 全局规则
- 两窗之外纯黑 Solid；棋盘格透明纹理严禁出现。
- 全屏粒子层：约 25 个白色 1-2px 点，alpha 0.3-0.8，缓慢下坠漂移，覆盖整屏（含两窗外黑边），
  默认开，设置可关（`persistent.particles`）。

### 布局（基准 1280×720，数值进 tokens）
- 图像窗：左右边距各 12% 宽；上边距 11% 高；高 57%；1px 边框 #cfcfcf；内显示抖动背景。
- 文本窗：左右边距同图像窗；上缘 71% 高；下缘距屏底 1%；1px 边框 #cfcfcf；内纯黑。
- 正文：左对齐，起始 x = 21% 屏宽；起始 y = 文本窗顶 + 8%；等宽 #e6e6e6 约 22px，行高 1.6，打字机。
- 微氛围：图像窗低频偶发 1 帧抖动噪点闪烁，默认开（`persistent.ambient_flicker`）。

### 快捷菜单（文本窗内部底端）
- 距窗底框约 10px，水平居中一行。
- 条目：BACK LOG SKIP AUTO SAVE Q.SAVE Q.LOAD SETTINGS（英文大写）。
- 等宽约 14px、字距 2、灰 #9a9a9a；不可用 #555555；hover #e6e6e6；条目间距约 3 字宽。

### 名字栏（who != null）
- 黑底 + 1px 边框 #cfcfcf；左缘 x ≈ 14%；宽随文字自适应；高约 8% 屏高。
- 竖向中心 = 图像窗底与文本窗顶之间的缝（骑缝）。
- 文本 "[NAME]" 等宽浅色居中，含方括号。

### 脸部框（who != null）
- 右侧方形说话人特写；右边距约 3%；宽约 16% 屏宽，近正方形。
- 上缘约 68% 高（骑文本窗上沿，伸入两窗黑缝）。
- 双层框：外 1px #cfcfcf，4px 黑缝，内 1px #cfcfcf；内显示脸图全彩。

### 立绘（有角色时）
- 全彩、不抖动、1-2px 亮描边；水平居中。
- 底边伸入图像窗底框下方约 2-3% 屏高的黑缝，不裁切。
- z-order：图像窗之上、名字栏/脸部框之下。

### 推进指示
- displayable 绘制红色小三角，打字机完成后出现于文本窗内右下，闪烁。

### who=null
- 隐藏名字栏/脸部框；正文切内心样式（#9a9a9a，约 20px）。

### 选择菜单
- 1px 浅色描边透明底按钮，居中纵列等宽留距。
- hover 反红底浅色字；0.1s 抖动入场。

### confirm 与系统屏幕
- confirm：全屏墨黑半透遮罩 + 居中线框小框，中文等宽"确定要退出吗？"，确定/返回线框按钮。
- yesno 类屏幕全部本地化改样（已在 options.rpy 覆盖 layout.* 字符串）。
- load/save/preferences 保留默认结构，仅用 gui 变量覆盖颜色/字体。

### fx 系统（9 旗标）
各 fx 为 ATL transform / 屏幕覆盖层，可由 `scene`/`show` 的 `at` 子句或屏幕标志触发。
JSON 解释器（已接线，逻辑不改）将 JSON 节点 `fx` 数组映射到这些效果。

| 旗标 | 说明 | JSON 示例 |
|------|------|-----------|
| `invert` | 反相颜色（RGB 255-x），持续 N 秒后恢复 | `{"fx":["invert"],"fx_dur":0.4}` |
| `shake` | 屏幕抖动（x/y 随机偏移衰减） | `{"fx":["shake"],"fx_dur":0.3}` |
| `flash` | 全屏白闪一帧后淡出 | `{"fx":["flash"],"fx_dur":0.2}` |
| `glitch` | RGB 通道分离 + 横向切片错位 | `{"fx":["glitch"],"fx_dur":0.25}` |
| `radio` | 强无线电噪点叠加（高频颗粒） | `{"fx":["radio"],"fx_dur":1.0}` |
| `radio_whisper` | 弱无线电噪点（低 alpha 颗粒） | `{"fx":["radio_whisper"],"fx_dur":2.0}` |
| `repeat` | 当前节点重复播放指定次数 | `{"fx":["repeat"],"repeat":3}` |
| `color_return` | 从当前 fx 状态平滑回正正常色 | `{"fx":["color_return"],"fx_dur":0.5}` |
| `sprite_dither` | 立绘切双色抖动模式（Bayer 4×4） | `{"fx":["sprite_dither"]}` |

### 背景资产
- 雪巷底图放入 `game/assets/bg/ref_snow_path.jpg`。
- 作为 ch01 与测试句默认背景；后续替换为自制无人雪巷资产。

## [S3] Out of Scope
- 标题屏代码改动（仅随 PALETTE token 切换外观）。
- 剧情 JSON 解释器逻辑改动（fx 旗标已设计为可被解释器调用的独立效果层）。
- 走路系统逻辑改动。
- 真实美术资产制作（立绘/脸图/背景均为占位）。
- 音乐音效接入。

## Tasks
- [x] T1: design_tokens.rpy 调色板 B 重定义 + 布局/组件令牌重写 — acceptance: PALETTE="B" 时 COL_ACCENT=#c1272d、COL_FRAME=#cfcfcf、COL_TEXT/#9a9a9a/#555555 可用；布局令牌按百分比 (covers: S2)
- [x] T2: 背景资产 ref_snow_path.jpg 复制 + image 定义 — acceptance: 文件存在于 game/assets/bg/，script 可 scene 引用 (covers: S2)
- [x] T3: say 屏重写（布局/名字栏/脸部框/立绘/推进三角/who=null） — acceptance: 骑缝名字栏、右侧双层脸部框、破框立绘、打字机后红三角闪烁、who=null 内心样式 (depends: T1; covers: S2)
- [x] T4: quick_menu 重写（英文大写/窗内底端/置灰） — acceptance: BACK LOG SKIP AUTO SAVE Q.SAVE Q.LOAD SETTINGS 居中于文本窗内底，#9a9a9a/#555555/#e6e6e6 (depends: T1,T3; covers: S2)
- [x] T5: choice 屏确认（1px 描边/hover 反红/0.1s 抖动入场） — acceptance: 透明底 1px 浅色描边，hover 红底浅字，choice_in 抖动 (depends: T1; covers: S2)
- [x] T6: 全屏粒子层 + preferences 开关 — acceptance: ~25 白点覆盖整屏含黑边，persistent.particles 控制开关 (depends: T1; covers: S2)
- [x] T7: fx 系统 9 旗标 ATL transforms + 调度 — acceptance: 9 个 fx 均可经 at 子句/标志触发并可视；DESIGN.md 各附说明 + JSON 示例 (depends: T1; covers: S2)
- [x] T8: confirm/yesno 本地化改样复查 — acceptance: 中文提示 + 线框按钮，layout.* 全覆盖 (covers: S2)
- [x] T9: script.rpy 测试内容更新（3 情况 + 新背景） — acceptance: 旁白/具名/选择三情况自玩覆盖，用 ref_snow_path 背景 (depends: T2,T3,T5; covers: S2)
- [x] T10: DESIGN.md 局内 UI 章节 + fx 文档 — acceptance: 含布局/组件/fx 9 旗标说明 + JSON 示例 (depends: T7; covers: S2)
- [x] T11: README TODO + lint 验证 — acceptance: README 含占位资产替换 TODO；lint 通过 (depends: T1-T10; covers: S2)
