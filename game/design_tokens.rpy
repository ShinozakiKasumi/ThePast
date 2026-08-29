################################################################################
# design_tokens.rpy — 设计令牌（单一可改源）
#
# 改 `PALETTE` 一个值即可在两套调色板间切换。所有颜色 / 字体 / 布局比例集中于此。
# gui.rpy 与 screens.rpy 只引用这里的 COL_* / FONT_* / LAYOUT_* 令牌。
#
# 线框档案风：纯黑底 · 1px 线框 · 双色抖动(1-bit)图像 · 等宽打字机字体 · 字距菜单
################################################################################

# 先于 gui.rpy(init offset -2) 加载，确保 COL_* / FONT_GROUP_* 可用。
init offset = -4

# ── 调色板切换 ──────────────────────────────────────────────────────────────
# "A" = 中式（墨黑/纸色/红笔红）   "B" = 局内（深/浅蓝灰 + 红强调 + 灰框线）
define PALETTE = "B"

# ── 调色板 A（中式）──────────────────────────────────────────────────────────
define PAL_A_BG    = "#0a0a0a"   # 墨黑（底色）
define PAL_A_PAPER = "#e6e0cf"   # 纸色（正文/框线）
define PAL_A_RED   = "#c1272d"   # 红笔红（强调/角色名/推进指示）
define PAL_A_GRAY  = "#6b6b6b"   # 灰（idle 菜单/内心独白）
define PAL_A_FRAME = "#e6e0cf"   # 框线 = 纸色
define PAL_A_TEXT  = "#e6e0cf"   # 正文 = 纸色
# 抖动双色 = 墨黑 + 纸色

# ── 调色板 B（局内）───────────────────────────────────────────────────────
define PAL_B_DARK   = "#05070a"   # 深（底色）
define PAL_B_LIGHT  = "#a8c0e8"   # 浅（标题/角色名等浅色元素）
define PAL_B_RED    = "#c1272d"   # 强调红（推进指示/选择 hover/fx）
define PAL_B_FRAME  = "#cfcfcf"   # 框线（中性灰，区别于浅蓝）
define PAL_B_TEXT   = "#e6e6e6"   # 正文（近白）
define PAL_B_GRAY   = "#5a6b8a"   # 灰蓝（idle/内心）
define PAL_B_QMGRAY = "#9a9a9a"   # 快捷菜单灰
define PAL_B_QMINSENS = "#555555" # 快捷菜单不可用
define PAL_B_QMHOVER = "#e6e6e6"  # 快捷菜单 hover
# 抖动双色 = 深 + 浅

# ── 活跃色（依 PALETTE 自动选择；条件表达式在 init 时求值）─────────────────────
define COL_BG       = PAL_A_BG    if PALETTE == "A" else PAL_B_DARK
define COL_PAPER    = PAL_A_PAPER if PALETTE == "A" else PAL_B_LIGHT
define COL_ACCENT   = PAL_A_RED   if PALETTE == "A" else PAL_B_RED
define COL_GRAY     = PAL_A_GRAY  if PALETTE == "A" else PAL_B_GRAY
define COL_FRAME    = PAL_A_FRAME if PALETTE == "A" else PAL_B_FRAME
define COL_TEXT     = PAL_A_TEXT  if PALETTE == "A" else PAL_B_TEXT
define COL_DITHER_D = PAL_A_BG    if PALETTE == "A" else PAL_B_DARK
define COL_DITHER_L = PAL_A_PAPER if PALETTE == "A" else PAL_B_LIGHT
# 快捷菜单专用色
define COL_QM_GRAY   = PAL_A_GRAY       if PALETTE == "A" else PAL_B_QMGRAY
define COL_QM_INSENS = (PAL_A_GRAY + "60") if PALETTE == "A" else PAL_B_QMINSENS
define COL_QM_HOVER  = PAL_A_PAPER      if PALETTE == "A" else PAL_B_QMHOVER
# 内心独白色（who=null）
define COL_INNER = COL_GRAY

# ── 字体路径 ────────────────────────────────────────────────────────────────
# 中文：Sarasa UI TC（更紗黑體 UI TC，思源黑体 CJK 字形 + Iosevka 拉丁；覆盖繁体）
# 拉丁：IBM Plex Mono（打字机风；FontGroup 让拉丁走 Plex、CJK 走 Sarasa）
define FONT_CJK       = "SarasaUiTC-Regular.ttf"
define FONT_CJK_BOLD  = "SarasaUiTC-Bold.ttf"
define FONT_LATIN     = "IBMPlexMono-Regular.ttf"
define FONT_LATIN_BOLD = "IBMPlexMono-Bold.ttf"
# 标题专用：NotoSansCJK TC Bold（最粗可用 CJK 字体，用于厚重主标题）
define FONT_TITLE_HEAVY = "NotoSansCJKTC-Bold.ttf"
# 标题菜单颜色：偏灰白色（非纯白）
define COL_MENU_TEXT = "#c8c8d0"

# ── FontGroup：拉丁走 IBM Plex Mono，CJK 走 Sarasa UI TC ────────────────────
init python:
    def _build_fontgroup(cjk, latin):
        return (
            FontGroup()
            .add(cjk, 0x2E80, 0x2FDF)    # CJK 部首/康熙部首
            .add(cjk, 0x3000, 0x303F)    # CJK 符号与标点
            .add(cjk, 0x3100, 0x312F)    # 注音符号
            .add(cjk, 0x31C0, 0x31EF)    # CJK 笔画
            .add(cjk, 0x3400, 0x4DBF)    # CJK 扩展 A
            .add(cjk, 0x4E00, 0x9FFF)    # CJK 统一表意文字
            .add(cjk, 0xF900, 0xFAFF)    # CJK 兼容表意文字
            .add(cjk, 0xFF00, 0xFFEF)    # 全角/半角形式
            .add(latin, None, None)      # 默认 = 拉丁
        )

    FONT_GROUP_REGULAR = _build_fontgroup(FONT_CJK, FONT_LATIN)
    FONT_GROUP_BOLD    = _build_fontgroup(FONT_CJK_BOLD, FONT_LATIN_BOLD)

# ── 布局比例（基准 1280×720，百分比 → 像素）──────────────────────────────────
# 图像窗：左右边距各 12% 宽；上边距 11% 高；高 57%
define IMG_MARGIN_X   = int(1280 * 0.12)          # 154
define IMG_WIN_X      = IMG_MARGIN_X              # 154
define IMG_WIN_Y      = int(720 * 0.11)           # 79 → 80（取整）
define IMG_WIN_W      = 1280 - 2 * IMG_MARGIN_X   # 972
define IMG_WIN_H      = int(720 * 0.57)           # 410
define IMG_WIN_BOTTOM = IMG_WIN_Y + IMG_WIN_H     # 490

# 文本窗：左右边距同图像窗；上缘 71% 高；下缘距屏底 1%
define TXT_WIN_X      = IMG_MARGIN_X              # 154
define TXT_WIN_Y      = int(720 * 0.71)           # 511
define TXT_WIN_W      = IMG_WIN_W                 # 972
define TXT_WIN_BOTTOM = 720 - int(720 * 0.01)     # 713
define TXT_WIN_H      = TXT_WIN_BOTTOM - TXT_WIN_Y # 202

# 接缝 Y = 图像窗底与文本窗顶的中点
define SEAM_Y         = (IMG_WIN_BOTTOM + TXT_WIN_Y) / 2   # 500

# 正文：起始 x = 21% 屏宽；起始 y = 文本窗顶 + 8% 屏高
define TEXT_START_X   = int(1280 * 0.21)         # 269
define TEXT_START_Y   = TXT_WIN_Y + int(720 * 0.08) # 511 + 57 = 568
define TEXT_SIZE      = 22
define TEXT_LINE_LEADING = 13                      # 行高 1.6 ≈ 22*0.6

# ── 名字栏（骑缝，who != null）──────────────────────────────────────────────
# 黑底 + 1px 框；左缘 x ≈ 14%；宽随文字（token 给默认值，可调）；高约 8% 屏高
define NAMEBOX_X      = int(1280 * 0.14)          # 179
define NAMEBOX_H      = int(720 * 0.08)           # 57 → 58
define NAMEBOX_Y      = SEAM_Y - NAMEBOX_H / 2     # 471
define NAMEBOX_W      = 200                        # 默认宽（token 可调）
define NAMEBOX_PAD    = 16                         # 文字左右内边距

# ── 脸部框（右侧方形，双层框，who != null）──────────────────────────────────
# 右边距约 3%；宽约 16% 屏宽，近正方形；上缘约 68% 高（骑文本窗上沿）
define FACEBOX_W      = int(1280 * 0.16)          # 204 → 205
define FACEBOX_H      = FACEBOX_W                 # 近正方形
define FACEBOX_RIGHT  = int(1280 * 0.03)          # 38
define FACEBOX_X      = 1280 - FACEBOX_RIGHT - FACEBOX_W  # 1037
define FACEBOX_Y      = int(720 * 0.68)           # 489 → 490
define FACEBOX_GAP    = 4                          # 外框与内框间黑缝

# ── 立绘（破框，全彩，不抖动）────────────────────────────────────────────────
# 水平居中；底边伸入图像窗底框下方约 2-3% 屏高的黑缝
define SPRITE_W       = 480
define SPRITE_H       = 440
define SPRITE_X       = (1280 - SPRITE_W) / 2     # 400
define SPRITE_BREAK   = int(720 * 0.025)          # 18px（2.5%）
define SPRITE_Y       = IMG_WIN_Y + IMG_WIN_H - SPRITE_H + SPRITE_BREAK  # 67

# ── 推进指示（文本窗内右下，打字机完成后出现）────────────────────────────────
define ADV_IND_X      = TXT_WIN_X + TXT_WIN_W - 30
define ADV_IND_Y      = TXT_WIN_Y + TXT_WIN_H - 26

# ── 快捷菜单（文本窗内部底端）────────────────────────────────────────────────
# 距窗底框约 10px，水平居中一行；大写等宽约 14px、字距 2
define QUICK_MENU_Y   = TXT_WIN_BOTTOM - 24       # 窗内底端约 10px 间隙
define QUICK_MENU_SIZE = 14
define QUICK_MENU_KERNING = 2
define QUICK_MENU_SPACING = 36                    # 约 3 字宽（14px × ~2.5）

# ── 全屏粒子层 ───────────────────────────────────────────────────────────────
define PARTICLE_COUNT  = 25
define PARTICLE_SIZE_MIN = 1
define PARTICLE_SIZE_MAX = 2

# ── 微氛围 ──────────────────────────────────────────────────────────────────
# persistent.ambient_flicker 由 preferences 屏开关；默认 True。
default persistent.ambient_flicker = True
# persistent.particles 由 preferences 屏开关；默认 True。
default persistent.particles = True
