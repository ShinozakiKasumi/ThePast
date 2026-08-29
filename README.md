# ThePast — 线框档案风视觉小说（Ren'Py 8）

心理恐怖视觉小说工程框架。
纯黑底、1px 线框、双色 Bayer 抖动图像、等宽打字机字体、字距菜单——整体"档案/终端"感。

## 运行

```bash
# 使用启动脚本（自动定位 Ren'Py 8 SDK；可用 RENPY_SDK 环境变量覆盖路径）
./run_game.sh            # 启动游戏
./run_game.sh lint       # lint 检查
python3 run_game.py      # Python 版本启动脚本

# 或直接使用 Ren'Py 8 SDK
$RENPY_SDK/renpy.sh .

# 或 lint 检查
$RENPY_SDK/renpy.sh . lint
```

## 切换调色板

编辑 `game/design_tokens.rpy`，修改一行：

```renpy
define PALETTE = "B"   # "A" = 中式（墨黑/纸色/红笔红）  "B" = 局内（深/浅蓝灰+红强调+灰框线）
```

所有颜色/框线/抖动双色/强调色自动切换。局内默认 B。

## 多语言支持

游戏支持两种语言：

| 语言 | 代码 | 说明 |
|------|------|------|
| 繁體中文 | `None`（基础语言） | 源码字符串即繁体中文 |
| English | `english` | 翻译文件在 `game/tl/english/` |

### 切换语言

在设置界面（preferences）的「語言 / Language」分区选择语言，即时生效。

### 翻译系统

- 所有用户可见字符串用 `_()` 包裹（Ren'Py 翻译函数）
- 基础语言为繁体中文，源码字符串即 TC
- 英文翻译在 `game/tl/english/` 目录：
  - `common.rpy` — UI 字符串翻译（菜单/按钮/标签/layout.* 提示）
  - `script.rpy` — 对话翻译（translate 块）
  - `options.rpy` — config.name 翻译
- 字体：Sarasa UI TC（覆盖繁体中文字形）

### 添加新翻译字符串

1. 在源码中用 `_("字符串")` 包裹新字符串
2. 运行 `renpy.sh <game_dir> translate english` 生成翻译骨架
3. 在 `game/tl/english/common.rpy` 中填入英文翻译

## 占位资产生成器

`tools/gen_placeholders.py` 生成三种占位资产（开发工具，运行时不依赖）：

```bash
# 背景占位（Bayer 4x4 双色抖动，暗示走廊/教室/校门夜景）
python3 tools/gen_placeholders.py --type bg

# 立绘占位（黑色人形剪影 + 2px 亮色描边、透明底）
python3 tools/gen_placeholders.py --type sprite

# 脸部框占位（方黑底 + 双层框 + 居中名字首字）
python3 tools/gen_placeholders.py --type face --name SNOW

# 切换调色板
python3 tools/gen_placeholders.py --type bg --palette B

# 批量处理真实照片为抖动风格（仅 bg 类型）
python3 tools/gen_placeholders.py --type bg --input photos/
```

调色板色值与 `game/design_tokens.rpy` 保持一致。

## 文件结构

```
ThePast/
├── run_game.py            # Python 启动脚本
├── run_game.sh            # Shell 启动脚本
├── game/
│   ├── design_tokens.rpy    # 设计令牌：PALETTE 切换 + 颜色/字体/布局/骑缝组件令牌
│   ├── options.rpy           # 项目配置：名称/版本/窗口/转场/音频钩子
│   ├── gui.rpy               # GUI 变量：颜色/字体/尺寸覆盖（引用 design_tokens 令牌）
│   ├── screens.rpy           # 屏幕：main_menu / say / choice / quick_menu + 默认屏幕
│   ├── script.rpy            # 测试标签：旁白/具名角色/选择三种情况
│   ├── fonts/                # Sarasa UI TC + IBM Plex Mono
│   ├── tl/english/           # 英文翻译（common.rpy + script.rpy + options.rpy）
│   └── assets/
│       ├── bg/               # 抖动占位背景（1280×720）
│       ├── sprites/          # 立绘占位（480×440，透明底）
│       └── faces/            # 脸部框占位（120×120，双层框）
├── tools/
│   ├── gen_placeholders.py   # 占位资产生成器（bg/sprite/face）
│   └── setup_fonts.py        # 字体提取工具（从 .ttc 提取 Mono CJK SC/TC 面为独立 OTF）
├── DESIGN.md                 # 局内 UI 设计文档 + fx 系统 9 旗标说明
└── docs/compose/spec/
    └── vn-in-game-ui.md      # 局内界面功能规格说明
```

## 屏幕说明

| 屏幕 | 说明 |
|------|------|
| `main_menu` | 标题《　》逐字出现 + 黄历风味块 + 5 项菜单（hover 强调色+位移） |
| `say` | 图像窗(1px框) + 文本窗(1px框纯黑底) + 名字栏(骑缝) + 脸部框(右侧双层框) + 立绘(破框) + ▼推进指示 |
| `choice` | 1px 描边透明底，hover 反红底纸色字，0.1s 抖动入场 |
| `quick_menu` | 文本窗内底端一行 8 项：回退/記錄/略過/自動/存檔/快儲/快讀/設定 |
| `game_menu` | 默认结构 + gui 颜色/字体覆盖 |
| `navigation` | 左侧导航（历史/保存/读取/设置/标题/退出） |
| `file_slots` | 存档/读档槽（3×2 网格 + 页面切换 + AUTO/QUICK 页） |
| `save` / `load` | 复用 file_slots |
| `preferences` | 語言/跳過/顯示/文字速度/自動前進/音量/微氛圍/粒子層 |
| `history` | 历史对话记录 |
| `yesno` / `notify` | 确认框（YES/NO）/ 通知 |
| `skip_indicator` | 跳过指示（SKIPPING... + 动画三角形） |

## say 屏数据接口

```renpy
screen say(who, what, face=None, sprite=None)
```

- `who`：角色名（字符串）；`None` 时为旁白，隐藏名字栏/脸部框/立绘
- `face`：脸部图 key（对应 `game/assets/faces/` 下的图像）
- `sprite`：立绘 key（对应 `game/assets/sprites/` 下的图像）

Character 通过 `show_face` / `show_sprite` 前缀将 face/sprite 传入 say 屏：

```renpy
define snow = Character("SNOW", show_face="face_snow", show_sprite="sprite_snow")
```

## 下一阶段计划（TODO）

- **剧情 JSON 解释器**：从 JSON 节点映射 `who`/`face`/`sprite` → Character 调用（已接线数据接口，逻辑待实现）
- **走路系统**：角色在场景中移动的路径/动画系统
- **真实立绘加亮描边**：`tools/gen_placeholders.py` 中 `process_sprite_outline()` 已预留
- **真实照片批量处理**：`--input` 接口已就绪
- **fx 系统对接**：9 旗标 ATL transforms 已就绪（见 `DESIGN.md` fx 章节），待 JSON 解释器调用
