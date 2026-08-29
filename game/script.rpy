################################################################################
# script.rpy — 雪夜返校开场（女主 Snow 立绘展示）
#
# 布局重构：立绘贴左缘 + 底部出血 + 压在对话框之上（front 层）
# 对话框居中、宽 54%（1035px），与立绘形成不对称平衡
################################################################################

## ── 通关旗标 ─────────────────────────────────────────────────────
default persistent.game_clear = False

## ── 背景图像 ────────────────────────────────────────────────────────────────
image bg corridor   = "assets/bg/bg_corridor.png"
image bg classroom  = "assets/bg/bg_classroom.png"
image bg gate_night = "assets/bg/bg_gate_night.png"
## 像素化雪路背景（640×360 降采样后 nearest 放大至 1920×1080）
image bg snow_path  = "assets/bg/snow_path_blur.png"

## ── 立绘（仅 thinking 表情用于测试新布局）────────────────────────────────────
image snow thinking = "assets/sprites/snow_thinking.png"

## ── 立绘定位 transform（1920×1080 坐标）──────────────────────────────────────
## 贴屏幕左缘（x=0），zoom 0.2 放大（2352×4006 → 470×801）
## yanchor 1.0 + ypos 1080：底部锚定屏幕底边，自然出血
## 在 front 层显示，压在对话框之上
transform sprite_pos:
    xpos 0
    yanchor 1.0
    ypos 1080
    zoom 0.2
    matrixcolor TintMatrix("#8090b8") * SaturationMatrix(0.65)

## ── 角色 ──────────────────────────────────────────────────────────────────────
define narrator = Character(None)
define snow = Character("SNOW", who_color="#a8c0e8")

## ── 开场标签 ──────────────────────────────────────────────────────────────────
label start:
    ## 雪夜返校背景（像素化版本）
    scene bg snow_path

    ## 旁白：雪夜氛围
    "十二月的雪落在肩上，悄無聲息地堆積。"
    "返校的路比記憶中漫長，每一步都踩進鬆軟的白裡。"

    ## Snow 出場（thinking 表情）— 立绘在 front 层，压在对话框之上
    show snow thinking at sprite_pos
    snow "……呼。終於快到了。"
    snow "鞋裡灌了雪，腳趾都快沒知覺了。"
    snow "學校這個時候應該已經沒人了吧。"
    snow "……回去之後，要做什麼呢。"
    snow "說不定教室的燈還亮著，像上次一樣。"
    snow "也好。一個人靜靜地待著，也不錯。"
    snow "至少雪還在下——這種景色，不討厭。"
    snow "……走吧。再不快點，真的要凍僵了。"

    return
