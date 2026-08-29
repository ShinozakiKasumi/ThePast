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
