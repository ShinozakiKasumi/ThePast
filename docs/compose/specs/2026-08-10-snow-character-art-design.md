# Snow 角色立绘插入设计

> [!NOTE]
> This document may not reflect the current implementation.
> See the final report for up-to-date state:
> [Final Report](../reports/snow-character-art.md)

## [S1] Problem

将新女主 Snow 的三张立绘（thinking / smile1 / normal2）插入 ThePast 游戏。需要：
1. 去除纯白背景 → 透明 PNG
2. 以多表情切换方式在游戏中显示
3. 开场场景使用雪夜返校背景

## [S2] Solution overview

三步：图像处理 → Ren'Py 立绘定义 → 开场场景脚本。

## [S3] 图像处理

- 输入：`~/Downloads/thinking`（1664×2496 JPEG）、`~/Downloads/smile1`（1440×2880 JPEG）、`~/Downloads/normal2`（1664×2496 JPEG）
- 工具：Python + Pillow + numpy（flood-fill 边缘去白 + 阈值透明化 + 抗锯齿）；ImageMagick 交叉验证
- 输出尺寸：缩放至高度 440px（保持比例），透明填充至 480×440 统一尺寸（水平居中）
- 输出路径：
  - `game/assets/sprites/snow_thinking.png`
  - `game/assets/sprites/snow_smile.png`
  - `game/assets/sprites/snow_normal.png`
- 脸部裁剪：从 normal 裁剪上部脸部区域 → `game/assets/faces/face_snow.png`（205×205）

## [S4] 立绘定义（多表情整图）

Snow 的立绘是整张全身图（非分层），采用多表情整图定义：

```renpy
image snow thinking = "assets/sprites/snow_thinking.png"
image snow smile     = "assets/sprites/snow_smile.png"
image snow normal    = "assets/sprites/snow_normal.png"
image face_snow      = "assets/faces/face_snow.png"
```

角色定义：
```renpy
define snow = Character("SNOW", show_face="face_snow", show_sprite="snow_normal")
```

表情切换：对话时用 `show_sprite=` 覆盖（适配 ThePast say 屏架构，say 屏全屏 Solid(COL_BG) 在 screens 层之上覆盖 master 层，故用 show_sprite 而非 show 语句）。

## [S5] 开场场景

- 背景：`scene bg snow_path at img_window_pos`（已有 `ref_snow_path.jpg`）
- 旁白：2-3 行雪夜返校氛围描写
- Snow 台词：normal → thinking → smile 三次切换
- 结束 `return` 回标题

## [S6] 文件变更

| 文件 | 变更 |
|------|------|
| `game/assets/sprites/snow_thinking.png` | 新建 |
| `game/assets/sprites/snow_smile.png` | 新建 |
| `game/assets/sprites/snow_normal.png` | 新建 |
| `game/assets/faces/face_snow.png` | 新建 |
| `game/script.rpy` | 修改：角色定义 + 立绘图像 + 开场场景 |
