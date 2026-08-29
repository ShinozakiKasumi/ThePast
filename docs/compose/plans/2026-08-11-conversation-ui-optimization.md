# Conversation UI Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize the conversation UI across three dimensions: art style fusion (background blur + sprite cold tint + repositioning), font/typography (anti-aliased font + name differentiation + padding), and dialog box/system buttons (full-width gradient + optimized quick menu).

**Architecture:** Generate new visual assets (blurred background, gradient dialog box) with Python/Pillow. Replace pixel font with SarasaUiTC FontGroup in gui.rpy. Restructure dialog box to full-width gradient in screens.rpy. Adjust sprite transform in script.rpy for cold tint and bottom anchoring on master layer.

**Tech Stack:** Ren'Py 8, Python/Pillow (asset generation), SarasaUiTC fonts (already in `game/fonts/`)

## Global Constraints

- Resolution: 1920×1080
- Ren'Py SDK: `./run_game.sh lint`
- Kill old renpy processes before launching: `kill -9 $(pgrep -f renpy)`
- Font: SarasaUiTC-Regular.ttf / SarasaUiTC-Bold.ttf (already in `game/fonts/`)
- FontGroup defined in `design_tokens.rpy` as `FONT_GROUP_REGULAR` / `FONT_GROUP_BOLD` (init offset -4, available before gui.rpy init offset -2)
- Color scheme: dark blue `#05070a`, ice blue `#a8c0e8`, text `#e6e6e6`, accent red `#c1272d`
- Sprite: `snow_thinking.png` 2352×4006, zoom 0.2 → 470×801px

---

### Task 1: Generate Visual Assets

**Covers:** Background blur + gradient dialog box

**Files:**
- Create: `game/assets/bg/snow_path_blur.png` (blurred background)
- Create: `game/gui/textbox_gradient.png` (full-width gradient dialog box)
- Create: `tools/gen_ui_assets.py` (generation script)

**Interfaces:**
- Produces: `snow_path_blur.png` (1920×1080 RGB) referenced by `script.rpy` Task 4
- Produces: `textbox_gradient.png` (1920×300 RGBA) referenced by `screens.rpy` Task 3

- [ ] **Step 1: Write asset generation script**

Create `tools/gen_ui_assets.py`:

```python
#!/usr/bin/env python3
"""Generate UI assets: blurred background + gradient dialog box."""
from PIL import Image, ImageFilter
import os

GAME_DIR = os.path.join(os.path.dirname(__file__), "..", "game")

def gen_blur_bg():
    """Apply Gaussian blur to snow_path_pixel.png."""
    src = os.path.join(GAME_DIR, "assets/bg/snow_path_pixel.png")
    dst = os.path.join(GAME_DIR, "assets/bg/snow_path_blur.png")
    img = Image.open(src).convert("RGB")
    blurred = img.filter(ImageFilter.GaussianBlur(radius=3))
    blurred.save(dst)
    print(f"Generated {dst}: {blurred.size}")

def gen_gradient_textbox():
    """Generate 1920×300 vertical gradient: transparent top → semi-transparent dark bottom."""
    w, h = 1920, 300
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pixels = img.load()
    for y in range(h):
        # Linear gradient: alpha 0 at top → 217 at bottom (~85% opacity)
        alpha = int(217 * (y / h))
        for x in range(w):
            pixels[x, y] = (5, 7, 10, alpha)  # #05070a
    dst = os.path.join(GAME_DIR, "gui/textbox_gradient.png")
    img.save(dst)
    print(f"Generated {dst}: {img.size}")

if __name__ == "__main__":
    gen_blur_bg()
    gen_gradient_textbox()
```

- [ ] **Step 2: Run the script**

Run: `python3 tools/gen_ui_assets.py`
Expected: Two files generated with correct dimensions.

- [ ] **Step 3: Verify generated files**

Run:
```bash
python3 -c "
from PIL import Image
for f in ['game/assets/bg/snow_path_blur.png', 'game/gui/textbox_gradient.png']:
    img = Image.open(f)
    print(f'{f}: {img.size} mode={img.mode}')
"
```
Expected: `snow_path_blur.png: (1920, 1080) mode=RGB` and `textbox_gradient.png: (1920, 300) mode=RGBA`

- [ ] **Step 4: Commit**

```bash
git add tools/gen_ui_assets.py game/assets/bg/snow_path_blur.png game/gui/textbox_gradient.png
git commit -m "feat: generate blurred background + gradient dialog box assets"
```

---

### Task 2: Font Replacement + Typography

**Covers:** Anti-aliased font, name differentiation, text padding

**Files:**
- Modify: `game/gui.rpy:58-79` (font + size variables)
- Modify: `game/gui.rpy:189-192` (quick button text styling)

**Interfaces:**
- Consumes: `FONT_GROUP_REGULAR` / `FONT_GROUP_BOLD` from `design_tokens.rpy` (init offset -4)
- Produces: `gui.text_font` = FontGroup (SarasaUiTC + IBM Plex Mono), `gui.name_text_size` = 42, `gui.quick_button_text_size` = 28

- [ ] **Step 1: Replace font references in gui.rpy**

In `game/gui.rpy`, replace lines 58-63:

```python
## The font used for in-game text.
define gui.text_font = gui.preference("font_1", "JF-Dot-Kappa20.ttf") 
## The font used for character names.
define gui.name_text_font = gui.preference("font_2", "JF-Dot-Kappa20B.ttf") 
## The font used for out-of-game text.
define gui.interface_text_font = "JF-Dot-Kappa20B.ttf"
```

With:

```python
## The font used for in-game text (SarasaUiTC + IBM Plex Mono FontGroup).
define gui.text_font = FONT_GROUP_REGULAR
## The font used for character names (bold variant).
define gui.name_text_font = FONT_GROUP_BOLD
## The font used for out-of-game text (bold variant).
define gui.interface_text_font = FONT_GROUP_BOLD
```

- [ ] **Step 2: Adjust font sizes for name differentiation**

In `game/gui.rpy`, replace lines 66-69:

```python
## The size of normal dialogue text.
define gui.text_size = 36

## The size of character names.
define gui.name_text_size = 36
```

With:

```python
## The size of normal dialogue text.
define gui.text_size = 36

## The size of character names (larger + bold for hierarchy).
define gui.name_text_size = 42
```

- [ ] **Step 3: Increase dialogue padding**

In `game/gui.rpy`, replace lines 131-135:

```python
define gui.dialogue_xpos = 100
define gui.dialogue_ypos = 80

## The maximum width of dialogue text, in pixels.
define gui.dialogue_width = 835
```

With:

```python
define gui.dialogue_xpos = 120
define gui.dialogue_ypos = 100

## The maximum width of dialogue text, in pixels.
define gui.dialogue_width = 1680
```

- [ ] **Step 4: Adjust name position for more padding**

In `game/gui.rpy`, replace lines 107-108:

```python
define gui.name_xpos = 100
define gui.name_ypos = 35
```

With:

```python
define gui.name_xpos = 120
define gui.name_ypos = 30
```

- [ ] **Step 5: Optimize quick button text styling**

In `game/gui.rpy`, replace lines 189-192:

```python
define gui.quick_button_borders = Borders(15, 6, 15, 0)
define gui.quick_button_text_size = 21
define gui.quick_button_text_idle_color = gui.idle_small_color
define gui.quick_button_text_selected_color = gui.accent_color
```

With:

```python
define gui.quick_button_borders = Borders(20, 6, 20, 0)
define gui.quick_button_text_size = 28
define gui.quick_button_text_idle_color = "#c8c8d0"
define gui.quick_button_text_hover_color = "#e6e6e6"
define gui.quick_button_text_selected_color = gui.accent_color
```

- [ ] **Step 6: Run lint to verify**

Run: `./run_game.sh lint`
Expected: No errors related to font or gui variables.

- [ ] **Step 7: Commit**

```bash
git add game/gui.rpy
git commit -m "feat: replace pixel font with SarasaUiTC + optimize typography (name hierarchy, padding, quick menu)"
```

---

### Task 3: Dialog Box + Namebox + Quick Menu Layout

**Covers:** Full-width gradient dialog box, namebox cleanup, quick menu repositioning

**Files:**
- Modify: `game/screens.rpy:166-196` (window + namebox + dialogue styles)
- Modify: `game/screens.rpy:305-314` (quick menu styles)

**Interfaces:**
- Consumes: `textbox_gradient.png` from Task 1
- Produces: Full-width (1920px) gradient dialog box at ypos 780, namebox with no background, quick menu at bottom right inside dialog box

- [ ] **Step 1: Update window style for full-width gradient**

In `game/screens.rpy`, replace the `style window` block (lines 166-172):

```python
style window:
    xalign 0.5
    xsize 1035
    ypos 740
    ysize gui.textbox_height

    background Image("gui/textbox_custom.png", xalign=0.5, yalign=0.0)
```

With:

```python
style window:
    xalign 0.5
    xsize 1920
    ypos 780
    ysize 300

    background Image("gui/textbox_gradient.png", xalign=0.5, yalign=0.0)
```

- [ ] **Step 2: Remove namebox background**

In `game/screens.rpy`, replace the `style namebox` block (lines 174-182):

```python
style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding
```

With:

```python
style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    ypos gui.name_ypos

    background None
```

- [ ] **Step 3: Reposition quick menu inside dialog box**

In `game/screens.rpy`, replace the `style quick_menu` block (lines 305-308):

```python
style quick_menu:
    xalign 1.0
    xpos 1380
    ypos 990
```

With:

```python
style quick_menu:
    xalign 1.0
    xpos 1840
    ypos 1020
    spacing 20
```

- [ ] **Step 4: Run lint to verify**

Run: `./run_game.sh lint`
Expected: No errors related to style changes.

- [ ] **Step 5: Commit**

```bash
git add game/screens.rpy
git commit -m "feat: full-width gradient dialog box + remove namebox bg + reposition quick menu"
```

---

### Task 4: Sprite Integration (Background Blur + Cold Tint + Repositioning)

**Covers:** Background blur reference, sprite cold blue overlay, sprite bottom anchoring on master layer

**Files:**
- Modify: `game/script.rpy:16` (background image reference)
- Modify: `game/script.rpy:25-29` (sprite_pos transform)
- Modify: `game/script.rpy:45` (show statement - remove onlayer front)

**Interfaces:**
- Consumes: `snow_path_blur.png` from Task 1
- Produces: Blurred background, sprite with cold blue tint on master layer, bottom-anchored to screen bottom

- [ ] **Step 1: Switch background to blurred version**

In `game/script.rpy`, replace line 16:

```renpy
image bg snow_path  = "assets/bg/snow_path_pixel.png"
```

With:

```renpy
image bg snow_path  = "assets/bg/snow_path_blur.png"
```

- [ ] **Step 2: Update sprite_pos transform with cold tint + bottom anchor**

In `game/script.rpy`, replace the `sprite_pos` transform (lines 25-29):

```renpy
transform sprite_pos:
    xpos 0
    yanchor 0.0
    ypos 320
    zoom 0.2
```

With:

```renpy
transform sprite_pos:
    xpos 0
    yanchor 1.0
    ypos 1080
    zoom 0.2
    matrixcolor TintMatrix("#8090b8") * SaturationMatrix(0.65)
```

- [ ] **Step 3: Move sprite from front layer to master layer**

In `game/script.rpy`, replace line 45:

```renpy
    show snow thinking at sprite_pos onlayer front
```

With:

```renpy
    show snow thinking at sprite_pos
```

- [ ] **Step 4: Run lint to verify**

Run: `./run_game.sh lint`
Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add game/script.rpy
git commit -m "feat: blurred background + sprite cold blue tint + bottom-anchored on master layer"
```

---

### Task 5: Final Verification

**Covers:** Full integration verification

- [ ] **Step 1: Kill old renpy processes**

Run: `kill -9 $(pgrep -f renpy) 2>/dev/null; sleep 1; ps aux | grep renpy | grep -v grep | wc -l`
Expected: `0` (no running renpy processes)

- [ ] **Step 2: Run full lint**

Run: `./run_game.sh lint`
Expected: No errors. Warnings about orphan translations are acceptable.

- [ ] **Step 3: Launch game for visual verification**

Run:
```bash
kill -9 $(pgrep -f renpy) 2>/dev/null; sleep 1
rm -f game/gui.rpyc game/screens.rpyc game/script.rpyc game/design_tokens.rpyc
./run_game.sh &
sleep 8
kill -9 $(pgrep -f renpy) 2>/dev/null
```
Expected: Game launches without crash (exit by kill after 8s timeout = success, not a crash).

- [ ] **Step 4: Take screenshot for visual verification**

Run:
```bash
kill -9 $(pgrep -f renpy) 2>/dev/null; sleep 1
rm -f game/*.rpyc
./run_game.sh &
sleep 5
spectacle -b -f -n -o /tmp/ui_optimization_check.png 2>/dev/null || true
kill -9 $(pgrep -f renpy) 2>/dev/null
```

Then verify the screenshot programmatically:
```bash
python3 -c "
from PIL import Image
img = Image.open('/tmp/ui_optimization_check.png')
print(f'Screenshot size: {img.size}')
# Check if dialog box area has gradient (bottom should be darker than top)
import numpy as np
arr = np.array(img)
h = arr.shape[0]
# Sample bottom 300px (dialog box area) vs top area
bottom = arr[h-300:h, :, :3].mean()
top = arr[:300, :, :3].mean()
print(f'Top brightness: {top:.1f}, Bottom brightness: {bottom:.1f}')
print(f'Bottom darker: {bottom < top}')
"
```
Expected: Screenshot captured, bottom area darker than top (gradient dialog box visible).

- [ ] **Step 5: Final commit if any cache files changed**

```bash
git add -A
git status
```
Expected: Clean working tree (or only .rpyc cache files, which should not be committed).
