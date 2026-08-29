#!/usr/bin/env python3
"""Generate title screen assets: noise pattern, film grain, faded bg, grunge mask."""
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
import os
import random

GAME_DIR = os.path.join(os.path.dirname(__file__), "..", "game")
BG_DIR = os.path.join(GAME_DIR, "assets/bg")
GUI_DIR = os.path.join(GAME_DIR, "gui")

# Title screen dimensions (1920×1080)
W, H = 1920, 1080
TITLE_SIDE_W = 423  # Left sidebar width


def gen_noise_pattern():
    """Generate subtle noise/dither pattern for left sidebar.
    423×1080 RGBA — replaces the soft ghost「過去」text.
    Toned down: mostly dark with sparse bright specks, low opacity.
    """
    w, h = TITLE_SIDE_W, H
    # Generate random noise
    noise = np.random.randint(0, 256, (h, w), dtype=np.uint8)

    # Sparse dithering: only the brightest noise values become visible specks
    # Most of the image stays dark (10), only top ~15% of noise → dim gray (60)
    dithered = np.where(noise > 210, 60, 10).astype(np.uint8)

    # Add a few larger faint blotches for organic variation
    blotches_small = np.random.randint(0, 256, (h // 4 + 1, w // 4 + 1), dtype=np.uint8)
    blotches = np.kron(blotches_small, np.ones((4, 4), dtype=np.uint8))[:h, :w]
    dithered = np.where(blotches > 240, 50, dithered)

    # Convert to RGBA
    img = Image.fromarray(dithered, mode='L')
    rgba = img.convert('RGBA')

    # Low alpha ~20% — subtle texture, not a dominant element
    alpha = np.full((h, w), 51, dtype=np.uint8)  # ~20% opacity
    rgba.putalpha(Image.fromarray(alpha, mode='L'))

    dst = os.path.join(BG_DIR, "title_noise.png")
    rgba.save(dst)
    print(f"Generated {dst}: {rgba.size}")


def gen_film_grain():
    """Generate 1920×1080 film grain overlay (fine noise at ~5% opacity).
    Subtle — barely visible, just adds a hint of texture.
    """
    # Generate fine grayscale noise
    noise = np.random.randint(0, 256, (H, W), dtype=np.uint8)
    img = Image.fromarray(noise, mode='L')

    # Convert to RGBA with ~5% opacity
    rgba = img.convert('RGBA')
    alpha = np.full((H, W), 13, dtype=np.uint8)  # ~5% opacity
    rgba.putalpha(Image.fromarray(alpha, mode='L'))

    dst = os.path.join(BG_DIR, "film_grain.png")
    rgba.save(dst)
    print(f"Generated {dst}: {rgba.size}")


def gen_faded_bg():
    """Reduce saturation and contrast of title_bg.png for faded photo look.
    Toned down: subtle desaturation, not extreme.
    """
    src = os.path.join(BG_DIR, "title_bg.png")
    dst = os.path.join(BG_DIR, "title_bg_faded.png")

    img = Image.open(src).convert("RGB")

    # Reduce saturation by 20% (subtle)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.80)

    # Reduce contrast by 10% (subtle)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(0.90)

    img.save(dst)
    print(f"Generated {dst}: {img.size}")


def gen_grunge_mask():
    """Generate a subtle grunge texture mask for the title text.
    1920×1080 RGBA — very faint mottled texture.
    Toned down: minimal scratches, mostly transparent.
    """
    # Start with random noise
    noise = np.random.randint(0, 256, (H, W), dtype=np.uint8)
    img = Image.fromarray(noise, mode='L')

    # Apply Gaussian blur for larger mottled regions
    img = img.filter(ImageFilter.GaussianBlur(radius=5))

    # Threshold: mostly opaque, only the darkest ~5% becomes transparent
    arr = np.array(img)
    mask = np.where(arr > 50, 255, 0).astype(np.uint8)

    # Very few scratches (20 instead of 80), thin
    scratch_img = Image.new('L', (W, H), 255)
    draw = ImageDraw.Draw(scratch_img)
    random.seed(42)
    for _ in range(20):
        x1 = random.randint(0, W)
        y1 = random.randint(0, H)
        x2 = x1 + random.randint(-60, 60)
        y2 = y1 + random.randint(-20, 20)
        draw.line([(x1, y1), (x2, y2)], fill=0, width=1)

    mask_arr = np.array(scratch_img)
    final_mask = np.minimum(mask, mask_arr)

    rgba = Image.fromarray(final_mask, mode='L').convert('RGBA')
    r, g, b, _ = rgba.split()
    rgba = Image.merge('RGBA', (r, g, b, Image.fromarray(final_mask, mode='L')))

    dst = os.path.join(BG_DIR, "title_grunge_mask.png")
    rgba.save(dst)
    print(f"Generated {dst}: {rgba.size}")


if __name__ == "__main__":
    gen_noise_pattern()
    gen_film_grain()
    gen_faded_bg()
    gen_grunge_mask()
    print("All title screen assets generated.")
