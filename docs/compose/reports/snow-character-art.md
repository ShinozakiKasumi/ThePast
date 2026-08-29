---
feature: snow-character-art
status: delivered
specs:
  - docs/compose/specs/2026-08-10-snow-character-art-design.md
plans:
  - docs/compose/plans/2026-08-10-snow-character-art.md
branch: main
commits: 5a052e3..3581ca1
---

# Snow 角色立绘插入 — Final Report

## What Was Built

将新女主 Snow 的三张立绘（thinking / smile / normal）正式插入 ThePast 游戏。三张原始 JPEG 立绘经过白底去除处理，转为透明背景 PNG，以多表情切换方式集成到 Ren'Py 脚本中。开场场景使用已有的雪夜返校背景，Snow 在雪夜中返校，通过 normal → thinking → smile 三种表情切换展示立绘系统。

## Architecture

### 图像处理管线（`tools/process_snow_sprites.py`）

Python + Pillow + numpy 脚本，对每张 JPEG 执行：
1. **边缘 flood-fill 去白底** — BFS 从图像四边出发，仅标记与边缘连通的近白像素（RGB ≥ 240）为透明，保留角色内部的白色区域
2. **边界抗锯齿** — 对透明/不透明边界的像素按白度渐变 alpha，消除硬边
3. **缩放填充** — 按高度 440px 等比缩放，透明填充至 480×440 居中
4. **脸部裁剪** — 从 normal 立绘上部 25% 区域裁剪 205×205 脸部图

### Ren'Py 立绘系统（`game/script.rpy`）

立绘为整张全身图（非分层），采用多表情整图定义而非 `layeredimage`：

```renpy
image snow thinking = "assets/sprites/snow_thinking.png"
image snow smile    = "assets/sprites/snow_smile.png"
image snow normal   = "assets/sprites/snow_normal.png"
image face_snow     = "assets/faces/face_snow.png"

define snow = Character("SNOW", show_face="face_snow", show_sprite="snow_normal")
```

表情切换通过 say 语句的 `show_sprite=` 关键字参数（需用括号语法）覆盖默认立绘：
```renpy
snow "學校這個時候應該已經沒人了吧。" (show_sprite="snow_thinking")
```

### 开场场景

`label start` 使用 `scene bg snow_path at img_window_pos` 显示雪夜背景，2 行旁白后 Snow 出场，通过 7 句台词展示 normal → thinking → smile → normal 四次表情切换。

### Design Decisions

- **Flood-fill 而非全局阈值去白** — 角色服装/配饰可能含白色区域，flood-fill 仅去除与边缘连通的背景白，保留角色内部白色
- **多表情整图而非 layeredimage** — `layeredimage` 需要分层素材（眉/眼/嘴独立图层）；Snow 的立绘是整张全身图，分层不现实，改用多表情整图定义
- **show_sprite= 括号语法** — Ren'Py say 语句的关键字参数必须用括号包裹（`snow "text" (show_sprite="...")`），裸 `show_sprite=` 会导致 lint 报 "end of line expected"

## Usage

启动游戏：
```bash
python3 run_game.py        # 启动游戏
python3 run_game.py lint   # lint 检查
```

重新处理立绘（如替换源图）：
```bash
python3 tools/process_snow_sprites.py
```

## Verification

- **图像处理**：3 张立绘输出 480×440 RGBA，透明度 67-70%（背景去除，角色保留）；脸部 205×205 RGBA
- **ImageMagick 交叉验证**：flood-fill 方法比 ImageMagick `-fuzz 20% -transparent white` 去除更多背景白（67% vs 32-52%），且不误删角色内部白色
- **Ren'Py lint**：通过，无错误（仅 orphan translation 警告，因翻译 ID 为手写非自动生成）
- **Ren'Py compile**：通过，无错误
- **游戏启动**：8 秒超时运行无报错（exit code 124 = timeout，非崩溃）

## Journey Log

- [lesson] Ren'Py say 语句的关键字参数必须用括号语法 `snow "text" (show_sprite="...")`，裸 `show_sprite=` 会被解析为语句结束后的非法 token
- [lesson] Flood-fill 边缘去白比全局阈值更安全 — 角色内部白色区域（如衣服高光）不会被误删

## Source Materials

| File | Role | Notes |
|------|------|-------|
| `docs/compose/specs/2026-08-10-snow-character-art-design.md` | 设计文档 | 三步方案：图像处理 → 立绘定义 → 开场场景 |
| `docs/compose/plans/2026-08-10-snow-character-art.md` | 实现计划 | 2 个任务，inline 执行 |
| `tools/process_snow_sprites.py` | 图像处理脚本 | 可复用，替换 IMAGES 列表即可处理新立绘 |
| `game/script.rpy` | 游戏脚本 | 立绘定义 + 角色定义 + 开场场景 |
| `game/tl/english/script.rpy` | 英文翻译 | 开场台词英文版 |
