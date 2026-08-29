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
# 源码 JPEG 放进项目根下的 raw_sprites/ 目录再运行本脚本。
REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO_ROOT / "raw_sprites"
SPRITE_DIR = REPO_ROOT / "game" / "assets" / "sprites"
FACE_DIR = REPO_ROOT / "game" / "assets" / "faces"

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
