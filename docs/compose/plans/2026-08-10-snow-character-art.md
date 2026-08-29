# Snow 角色立绘插入 Implementation Plan

> [!NOTE]
> This document may not reflect the current implementation.
> See the final report for up-to-date state:
> [Final Report](../reports/snow-character-art.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将新女主 Snow 的三张立绘去白底后插入 ThePast 游戏，支持多表情切换，并撰写雪夜返校开场场景。

**Architecture:** Python+Pillow+numpy 脚本处理 JPEG → 透明 PNG（flood-fill 边缘去白 + 缩放填充至 480×440）；Ren'Py script.rpy 定义多表情立绘图像 + Character show_sprite 覆盖切换表情；开场场景使用已有雪巷背景。

**Tech Stack:** Python 3, Pillow, numpy, ImageMagick 7（交叉验证）, Ren'Py 8

## Global Constraints

- 立绘输出尺寸：480×440 px（高度 440px 保持比例，透明填充至 480px 宽居中）
- 脸部裁剪尺寸：205×205 px
- 白色阈值：RGB 各通道 ≥ 240 视为"近白"
- 角色名："SNOW"（全大写）
- 立绘文件命名：`snow_thinking.png`、`snow_smile.png`、`snow_normal.png`
- 脸部文件命名：`face_snow.png`
- Ren'Py SDK 路径：`~/renpy-8.5.3-sdk`
- 验证命令：`python3 run_game.py lint`

---

### Task 1: 图像处理 — 去白底 + 透明 PNG + 脸部裁剪

**Covers:** [S3]

**Files:**
- Create: `tools/process_snow_sprites.py`
- Create: `game/assets/sprites/snow_thinking.png`
- Create: `game/assets/sprites/snow_smile.png`
- Create: `game/assets/sprites/snow_normal.png`
- Create: `game/assets/faces/face_snow.png`

**Interfaces:**
- Consumes: `~/Downloads/thinking`（JPEG 1664×2496）、`~/Downloads/smile1`（JPEG 1440×2880）、`~/Downloads/normal2`（JPEG 1664×2496）
- Produces: 3 张 480×440 透明 PNG + 1 张 205×205 脸部 PNG

- [ ] **Step 1: 编写图像处理脚本**

Create `tools/process_snow_sprites.py`:

```python
#!/usr/bin/env python3
"""Remove white background from Snow's character art → transparent PNGs.

Flood-fill from image edges to remove only the background white (not white
areas within the character). Anti-alias boundary pixels. Scale to 440px
height, pad to 480×440 centered. Crop face from normal sprite.
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

# ── Configuration ──────────────────────────────────────────────────────
INPUT_DIR = Path("raw_sprites")
SPRITE_DIR = Path("game/assets/sprites")
FACE_DIR = Path("game/assets/faces")

IMAGES = [
    ("thinking", "snow_thinking.png"),
    ("smile1", "snow_smile.png"),
    ("normal2", "snow_normal.png"),
]

WHITE_THRESHOLD = 240   # RGB ≥ this → "near-white"
TARGET_W = 480
TARGET_H = 440
FACE_SIZE = 205


def remove_white_background(img: Image.Image) -> Image.Image:
    """Flood-fill from edges: mark near-white pixels connected to border as transparent."""
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]

    # White mask: True where all RGB channels ≥ threshold
    white_mask = np.all(arr >= WHITE_THRESHOLD, axis=2)

    # BFS flood-fill from border pixels that are white
    visited = np.zeros((h, w), dtype=bool)
    queue = deque()

    for x in range(w):
        for y_edge in (0, h - 1):
            if white_mask[y_edge, x] and not visited[y_edge, x]:
                visited[y_edge, x] = True
                queue.append((y_edge, x))
    for y in range(h):
        for x_edge in (0, w - 1):
            if white_mask[y, x_edge] and not visited[y, x_edge]:
                visited[y, x_edge] = True
                queue.append((y, x_edge))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while queue:
        cy, cx = queue.popleft()
        for dy, dx in dirs:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and white_mask[ny, nx]:
                visited[ny, nx] = True
                queue.append((ny, nx))

    # Alpha: 255 opaque by default, 0 for flood-filled background
    alpha = np.full((h, w), 255, dtype=np.uint8)
    alpha[visited] = 0

    # Anti-alias: for opaque pixels adjacent to transparent, fade alpha by whiteness
    # Shift visited mask in 4 directions to find boundary
    neighbor_transparent = np.zeros((h, w), dtype=bool)
    neighbor_transparent[1:, :] |= visited[:-1, :]
    neighbor_transparent[:-1, :] |= visited[1:, :]
    neighbor_transparent[:, 1:] |= visited[:, :-1]
    neighbor_transparent[:, :-1] |= visited[:, 1:]

    boundary = neighbor_transparent & ~visited  # opaque pixels next to transparent

    for y, x in np.argwhere(boundary):
        avg = arr[y, x].mean()
        if avg >= WHITE_THRESHOLD:
            alpha[y, x] = 0
        elif avg >= WHITE_THRESHOLD - 40:
            ratio = (avg - (WHITE_THRESHOLD - 40)) / 40.0
            alpha[y, x] = int(255 * (1.0 - ratio))

    rgba = np.dstack([arr, alpha])
    return Image.fromarray(rgba, "RGBA")


def scale_and_pad(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Scale to target height (maintain aspect), pad to target_w centered transparent."""
    w, h = img.size
    scale = target_h / h
    new_w = int(round(w * scale))
    img = img.resize((new_w, target_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    x_offset = (target_w - new_w) // 2
    canvas.paste(img, (x_offset, 0), img)
    return canvas


def crop_face(img: Image.Image, face_size: int) -> Image.Image:
    """Crop face region from upper portion of a 480×440 sprite."""
    w, h = img.size
    # Face occupies roughly top 25% of a full-body portrait
    face_h = int(h * 0.25)
    face_w = face_h  # square
    face_x = max(0, (w - face_w) // 2)
    face_y = int(h * 0.02)

    face = img.crop((face_x, face_y, face_x + face_w, face_y + face_h))
    return face.resize((face_size, face_size), Image.LANCZOS)


def main():
    SPRITE_DIR.mkdir(parents=True, exist_ok=True)
    FACE_DIR.mkdir(parents=True, exist_ok=True)

    for input_name, output_name in IMAGES:
        input_path = INPUT_DIR / input_name
        if not input_path.exists():
            print(f"ERROR: {input_path} not found", file=sys.stderr)
            sys.exit(1)

        print(f"Processing {input_name} → {output_name}")
        img = Image.open(input_path)
        print(f"  Original size: {img.size}")

        img = remove_white_background(img)
        img = scale_and_pad(img, TARGET_W, TARGET_H)
        output_path = SPRITE_DIR / output_name
        img.save(output_path, "PNG")
        print(f"  Saved: {output_path} ({img.size})")

        # Count transparent pixels for sanity check
        arr = np.array(img)
        transparent = (arr[:, :, 3] == 0).sum()
        total = arr.shape[0] * arr.shape[1]
        print(f"  Transparency: {transparent}/{total} pixels ({100*transparent/total:.1f}%)")

        # Face crop from normal
        if input_name == "normal2":
            face = crop_face(img, FACE_SIZE)
            face_path = FACE_DIR / "face_snow.png"
            face.save(face_path, "PNG")
            print(f"  Face crop: {face_path} ({face.size})")

    print("\nDone! All sprites processed.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行脚本处理三张立绘**

Run: `python3 tools/process_snow_sprites.py`
Expected: 3 PNG files created in `game/assets/sprites/`, 1 face PNG in `game/assets/faces/`. Transparency should be 40-70% (background removed, character retained).

- [ ] **Step 3: 用 ImageMagick 交叉验证去白底效果**

Run ImageMagick on each image for comparison:
```bash
for img in thinking smile1 normal2; do
  convert "raw_sprites/$img" -fuzz 20% -transparent white "/tmp/${img}_im.png"
  python3 -c "
from PIL import Image
import numpy as np
im = np.array(Image.open('/tmp/${img}_im.png').convert('RGBA'))
t = (im[:,:,3]==0).sum()
print(f'ImageMagick ${img}: {t}/{im.shape[0]*im.shape[1]} transparent ({100*t/(im.shape[0]*im.shape[1]):.1f}%)')
"
done
```
Compare transparency ratios. If ImageMagick's result is significantly better (cleaner edges, less halo), re-process using ImageMagick output as input to the scale_and_pad step.

- [ ] **Step 4: 验证输出文件**

Run:
```bash
python3 -c "
from PIL import Image
import numpy as np
for name in ['snow_thinking', 'snow_smile', 'snow_normal']:
    im = Image.open(f'game/assets/sprites/{name}.png')
    arr = np.array(im)
    t = (arr[:,:,3]==0).sum()
    total = arr.shape[0]*arr.shape[1]
    print(f'{name}.png: {im.size} mode={im.mode} transparency={100*t/total:.1f}%')
face = Image.open('game/assets/faces/face_snow.png')
print(f'face_snow.png: {face.size} mode={face.mode}')
"
```
Expected: All sprites 480×440 RGBA with 40-70% transparency. Face 205×205 RGBA.

- [ ] **Step 5: Commit**

```bash
git add tools/process_snow_sprites.py game/assets/sprites/snow_thinking.png game/assets/sprites/snow_smile.png game/assets/sprites/snow_normal.png game/assets/faces/face_snow.png
git commit -m "feat: process Snow character sprites — remove white background, create transparent PNGs"
```

---

### Task 2: 更新 script.rpy — 立绘定义 + 开场场景

**Covers:** [S4], [S5]

**Files:**
- Modify: `game/script.rpy` (full rewrite of image definitions, character, and label start)

**Interfaces:**
- Consumes: `game/assets/sprites/snow_thinking.png`, `snow_smile.png`, `snow_normal.png` (from Task 1)
- Consumes: `game/assets/faces/face_snow.png` (from Task 1)
- Consumes: `game/assets/bg/ref_snow_path.jpg` (already exists)
- Consumes: design tokens `IMG_WIN_X`, `IMG_WIN_Y`, `IMG_WIN_W`, `IMG_WIN_H`, `SPRITE_X`, `SPRITE_Y`, `SPRITE_W`, `SPRITE_H` from `design_tokens.rpy`
- Produces: playable opening scene with Snow character on snowy road background

- [ ] **Step 1: 重写 script.rpy**

Replace entire content of `game/script.rpy` with:

```renpy
################################################################################
# script.rpy — 雪夜返校开场（女主 Snow 立绘展示）
#
# 多表情切换方式：
#   snow "台词" show_sprite="snow_smile"  (适配 say 屏架构)
#
# 数据接口（为下一阶段剧情 JSON 解释器预留）：
#   Character 通过 show_face / show_sprite 前缀将 face/sprite 传入 say 屏。
################################################################################

## ── 背景图像 ────────────────────────────────────────────────────────────────
image bg corridor   = "assets/bg/bg_corridor.png"
image bg classroom  = "assets/bg/bg_classroom.png"
image bg gate_night = "assets/bg/bg_gate_night.png"
## 雪巷背景（开场用；图中两剪影为参考占位，发布版替换为自制资产）
image bg snow_path  = "assets/bg/ref_snow_path.jpg"

## ── 立绘（多表情整图定义）──────────────────────────────────────────
## Snow 为整张全身图，采用多表情整图定义。
image snow thinking = "assets/sprites/snow_thinking.png"
image snow smile    = "assets/sprites/snow_smile.png"
image snow normal   = "assets/sprites/snow_normal.png"

## ── 脸部图（say 屏右侧脸部框用）──────────────────────────────────────────────
image face_snow     = "assets/faces/face_snow.png"

## ── 角色 ──────────────────────────────────────────────────────────────────────
## who=null 时为旁白/内心独白（灰色更小样式，由 say 屏处理）
## show_face / show_sprite 前缀 → Ren'Py 将 face/sprite 作为 kwargs 传入 say 屏
## 默认立绘 snow_normal；对话时用 show_sprite="snow_thinking" 等覆盖切换表情
define narrator = Character(None)
define snow = Character("SNOW", show_face="face_snow", show_sprite="snow_normal")

## ── 开场标签 ──────────────────────────────────────────────────────────────────
label start:
    ## 雪夜返校背景
    if persistent.ambient_flicker:
        scene bg snow_path at img_window_pos, ambient_flicker
    else:
        scene bg snow_path at img_window_pos

    ## 旁白：雪夜氛围
    "十二月的雪落在肩上，悄無聲息地堆積。"
    "返校的路比記憶中漫長，每一步都踩進鬆軟的白裡。"

    ## Snow 出場（normal 表情）
    snow "……呼。終於快到了。"
    snow "鞋裡灌了雪，腳趾都快沒知覺了。" show_sprite="snow_normal"

    ## 切換 thinking 表情
    snow "學校這個時候應該已經沒人了吧。" show_sprite="snow_thinking"
    snow "……回去之後，要做什麼呢。"
    snow "說不定教室的燈還亮著，像上次一樣。" show_sprite="snow_thinking"

    ## 切換 smile 表情
    snow "也好。一個人靜靜地待著，也不錯。" show_sprite="snow_smile"
    snow "至少雪還在下——這種景色，不討厭。" show_sprite="snow_smile"

    ## 回 normal
    snow "……走吧。再不快點，真的要凍僵了。" show_sprite="snow_normal"

    return
```

- [ ] **Step 2: 运行 lint 检查**

Run: `python3 run_game.py lint`
Expected: No errors. Warnings about missing images are OK if they reference old assets not used in the new script. The key images (snow_thinking, snow_smile, snow_normal, face_snow, bg snow_path) should all resolve.

- [ ] **Step 3: 验证图像定义可被 Ren'Py 解析**

Run:
```bash
python3 -c "
import os, sys
sdk = os.path.expanduser('~/renpy-8.5.3-sdk')
sys.path.insert(0, os.path.join(sdk, 'lib/py3-linux-x86_64'))
# Just check the script parses by looking for syntax issues
with open('game/script.rpy') as f:
    content = f.read()
# Check key definitions exist
assert 'image snow thinking' in content, 'Missing snow thinking definition'
assert 'image snow smile' in content, 'Missing snow smile definition'
assert 'image snow normal' in content, 'Missing snow normal definition'
assert 'image face_snow' in content, 'Missing face_snow definition'
assert 'define snow = Character' in content, 'Missing snow Character definition'
assert 'show_sprite=\"snow_thinking\"' in content, 'Missing thinking expression switch'
assert 'show_sprite=\"snow_smile\"' in content, 'Missing smile expression switch'
assert 'scene bg snow_path' in content, 'Missing snow_path background'
print('All definitions present in script.rpy')
"
```
Expected: "All definitions present in script.rpy"

- [ ] **Step 4: 验证图像文件存在且可读**

Run:
```bash
python3 -c "
from PIL import Image
from pathlib import Path
files = [
    'game/assets/sprites/snow_thinking.png',
    'game/assets/sprites/snow_smile.png',
    'game/assets/sprites/snow_normal.png',
    'game/assets/faces/face_snow.png',
    'game/assets/bg/ref_snow_path.jpg',
]
for f in files:
    p = Path(f)
    assert p.exists(), f'Missing: {f}'
    im = Image.open(p)
    print(f'{f}: {im.size} {im.mode} OK')
print('All image files verified.')
"
```
Expected: All files exist with correct sizes and modes.

- [ ] **Step 5: Commit**

```bash
git add game/script.rpy
git commit -m "feat: insert Snow character sprites with expression switching and snowy night opening scene"
```
