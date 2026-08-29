#!/usr/bin/env python3
"""gen_placeholders.py — 占位资产生成器（开发工具，运行时不依赖）

支持三种类型（--type bg|sprite|face）：

bg     — Bayer 4x4 双色抖动占位背景（抽象渐变+噪点，暗示"走廊/教室/校门夜景"）
         也支持 --input DIR 批量处理真实照片：灰度→对比→Bayer→双色→噪点

sprite — 黑色人形剪影 + 1-2px 亮色描边、透明底 → game/assets/sprites/
         预留 process_sprite_outline() 处理真实立绘"加亮描边"

face   — 方黑底 + 双层 1px 框 + 居中名字首字 → game/assets/faces/

调色板色值必须与 game/design_tokens.rpy 保持一致。

Usage:
    python3 tools/gen_placeholders.py                              # bg: 3 张默认占位
    python3 tools/gen_placeholders.py --type sprite                # 立绘占位
    python3 tools/gen_placeholders.py --type face --name SNOW      # 脸部框占位
    python3 tools/gen_placeholders.py --palette B                  # 切调色板
    python3 tools/gen_placeholders.py --input photos/              # 处理真实照片(bg)
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── 调色板（须与 game/design_tokens.rpy 一致）──────────────────────────────
PALETTES = {
    "A": {"dark": (0x0a, 0x0a, 0x0a), "light": (0xe6, 0xe0, 0xcf), "accent": (0xc1, 0x27, 0x2d)},
    "B": {"dark": (0x05, 0x07, 0x0a), "light": (0xa8, 0xc0, 0xe8), "accent": (0xa8, 0xc0, 0xe8)},
}

# ── Bayer 4x4 有序抖动矩阵（归一化到 [0,1)）────────────────────────────────
BAYER_4 = np.array([
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5],
], dtype=np.float32) / 16.0


def bayer_dither(gray01):
    """gray01: HxW float [0,1] → HxW bool（True=浅色）。Bayer 4x4 有序抖动。"""
    h, w = gray01.shape
    bh, bw = BAYER_4.shape
    tiled = np.tile(BAYER_4, (h // bh + 1, w // bw + 1))[:h, :w]
    return gray01 > tiled


def to_dualcolor(mask, dark, light):
    """mask: HxW bool → HxWx3 uint8（dark/light 两色）。"""
    return np.where(mask[..., None], light, dark).astype(np.uint8)


def save_png(arr_rgb, path):
    Image.fromarray(arr_rgb, "RGB").save(str(path))


# ── 场景生成器：返回 HxW float [0,1] 灰度"高度图" ────────────────────────────

def gen_corridor(w, h, rng):
    """走廊：中央亮（尽头光源），上下暗（透视纵深）+ 竖纹（门/柱）。"""
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    v = 1.0 - np.abs(y - 0.45) * 1.8          # 中段偏亮
    v = np.broadcast_to(v, (h, w)).copy()
    x = np.arange(w, dtype=np.float32)[None, :]
    v += 0.12 * np.sin(x * 0.025 + rng.random() * 6)   # 竖纹
    v += 0.08 * np.sin(x * 0.004)                        # 远近渐变微调
    v += rng.normal(0, 0.04, (h, w))                     # 噪点
    return np.clip(v, 0, 1)


def gen_classroom(w, h, rng):
    """教室：横带——上亮（窗）、中（墙/黑板）、下暗（课桌/地）。"""
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    v = np.where(y < 0.30, 0.70,                       # 窗带
        np.where(y < 0.62, 0.35, 0.12))                 # 墙带 / 地带
    v = np.broadcast_to(v, (h, w)).copy()
    # 黑板矩形高亮
    v[ int(h*0.32):int(h*0.50), int(w*0.30):int(w*0.70)] += 0.20
    x = np.arange(w, dtype=np.float32)[None, :]
    v += 0.05 * np.sin(x * 0.05)                        # 窗格竖纹
    v += rng.normal(0, 0.04, (h, w))
    return np.clip(v, 0, 1)


def gen_gate_night(w, h, rng):
    """校门夜景：极暗 + 中央竖亮带（门口灯光）+ 稀疏噪点（星/灯）。"""
    v = np.full((h, w), 0.08, dtype=np.float32)
    x = np.arange(w, dtype=np.float32)[None, :]
    gate = np.exp(-((x - w * 0.5) ** 2) / (w * 28.0))   # 中央高斯亮带
    v += 0.55 * gate
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    v *= 1.0 - y * 0.3                                   # 上暗下稍亮
    # 稀疏亮点
    stars = (rng.random((h, w)) > 0.998).astype(np.float32) * 0.6
    v += stars
    v += rng.normal(0, 0.03, (h, w))
    return np.clip(v, 0, 1)


SCENES = {
    "bg_corridor":   gen_corridor,
    "bg_classroom":  gen_classroom,
    "bg_gate_night": gen_gate_night,
}


# ── 真实照片处理（--input）──────────────────────────────────────────────────

def process_photo(path, w, h, rng):
    """照片 → 灰度 → 对比拉伸 → 降采样 → 噪点 → 返回 [0,1] 灰度。"""
    img = Image.open(path).convert("L").resize((w, h), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    lo, hi = float(arr.min()), float(arr.max())
    arr = (arr - lo) / (hi - lo + 1e-6)                  # 对比拉伸
    arr += rng.normal(0, 0.03, arr.shape)                # 噪点
    return np.clip(arr, 0, 1)


# ── 立绘占位（sprite）─────────────────────────────────────────────────────────

def gen_sprite_silhouette(w, h):
    """返回 RGBA 图像：黑色人形剪影 + 2px 亮色描边、透明底。"""
    # 1. 在灰度遮罩上画人形剪影（白色=剪影区域）
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    cx = w // 2

    # 头部：椭圆
    head_r = int(w * 0.10)
    head_cy = int(h * 0.13)
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=255)

    # 颈部
    d.rectangle([cx - 12, head_cy + head_r - 5, cx + 12, head_cy + head_r + 25], fill=255)

    # 躯干：梯形（肩宽腰窄）
    shoulder_y = head_cy + head_r + 20
    waist_y = int(h * 0.62)
    shoulder_w = int(w * 0.22)
    waist_w = int(w * 0.16)
    d.polygon([
        (cx - shoulder_w, shoulder_y),
        (cx + shoulder_w, shoulder_y),
        (cx + waist_w, waist_y),
        (cx - waist_w, waist_y),
    ], fill=255)

    # 手臂：从肩部下垂
    arm_w = int(w * 0.07)
    d.rectangle([cx - shoulder_w - arm_w, shoulder_y, cx - shoulder_w, waist_y + 10], fill=255)
    d.rectangle([cx + shoulder_w, shoulder_y, cx + shoulder_w + arm_w, waist_y + 10], fill=255)

    # 腿部：从腰部到底部
    leg_w = int(w * 0.10)
    gap = 8
    d.rectangle([cx - leg_w - gap, waist_y, cx - gap, h], fill=255)
    d.rectangle([cx + gap, waist_y, cx + leg_w + gap, h], fill=255)

    # 2. 膨胀遮罩 → 减去原遮罩 = 描边区域（2px）
    dilated = mask.filter(ImageFilter.MaxFilter(5))
    outline_mask = Image.fromarray(
        np.array(dilated, dtype=np.uint8) - np.array(mask, dtype=np.uint8)
    )

    # 3. 合成 RGBA：剪影=黑、描边=亮色、其余透明
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    black = (0, 0, 0, 255)
    img.paste(black, mask=mask)
    return img, outline_mask


def gen_sprite(w, h, pal, name="sprite"):
    """生成立绘占位：黑色剪影 + 2px 亮色描边、透明底。"""
    img, outline_mask = gen_sprite_silhouette(w, h)
    accent = pal["accent"] + (255,)
    img.paste(accent, mask=outline_mask)
    return img


def process_sprite_outline(path, w, h, pal):
    """预留：真实立绘"加亮描边"处理函数。

    未来流程：抠图(透明底) → 提取 alpha 边缘 → 亮色描边 → 输出 RGBA。
    当前仅占位，不实际处理。
    """
    # TODO(真实立绘): 实现真实立绘的亮色描边处理
    # 1. 加载图片，抠图为透明底
    # 2. 提取 alpha 通道边缘（膨胀 - 腐蚀 = 边缘）
    # 3. 边缘填充亮色（accent）
    # 4. 合成输出
    raise NotImplementedError("process_sprite_outline 预留，待真实立绘阶段实现")


# ── 脸部框占位（face）─────────────────────────────────────────────────────────

def gen_face(w, h, pal, name="A"):
    """生成脸部框占位：方黑底 + 双层 1px 框 + 居中名字首字。

    尺寸 = FACEBOX_SIZE × FACEBOX_SIZE（默认 120×120）。
    双层框：外框 1px + 内框 1px（留 4px 缝），框色 = 调色板浅色。
    居中首字：亮色等宽字。
    """
    img = Image.new("RGB", (w, h), pal["dark"])
    d = ImageDraw.Draw(img)
    frame = pal["light"]
    accent = pal["accent"]

    # 外框 1px
    d.rectangle([0, 0, w - 1, h - 1], outline=frame, width=1)
    # 内框 1px（留 4px 缝）
    gap = 4
    d.rectangle([gap, gap, w - 1 - gap, h - 1 - gap], outline=frame, width=1)

    # 居中名字首字
    font = _load_face_font(h)
    initial = name[0].upper() if name else "?"
    bbox = d.textbbox((0, 0), initial, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (w - tw) // 2 - bbox[0]
    ty = (h - th) // 2 - bbox[1]
    d.text((tx, ty), initial, fill=accent, font=font)

    return img


def _load_face_font(size):
    """加载脸部框首字字体（IBM Plex Mono Bold，回退默认）。"""
    candidates = [
        "game/fonts/IBMPlexMono-Bold.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, int(size * 0.45))
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# ── 主流程 ────────────────────────────────────────────────────────────────────

TYPE_OUT_DIRS = {
    "bg": "game/assets/bg",
    "sprite": "game/assets/sprites",
    "face": "game/assets/faces",
}

TYPE_DEFAULT_SIZE = {
    "bg": [1280, 720],
    "sprite": [480, 440],
    "face": [120, 120],
}


def main():
    ap = argparse.ArgumentParser(description="占位资产生成器（bg/sprite/face）")
    ap.add_argument("--type", default="bg", choices=["bg", "sprite", "face"],
                    help="资产类型")
    ap.add_argument("--palette", default="A", choices=PALETTES)
    ap.add_argument("--size", type=int, nargs=2, default=None, metavar=("W", "H"),
                    help="输出尺寸（默认依 --type）")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None, help="输出目录（默认依 --type）")
    ap.add_argument("--input", default=None, metavar="DIR",
                    help="批量处理真实照片目录（仅 --type bg）")
    ap.add_argument("--name", default="A", help="脸部框首字（仅 --type face）")
    args = ap.parse_args()

    # 默认值依 --type
    if args.size is None:
        args.size = TYPE_DEFAULT_SIZE[args.type]
    if args.out is None:
        args.out = TYPE_OUT_DIRS[args.type]

    w, h = args.size
    rng = np.random.default_rng(args.seed)
    pal = PALETTES[args.palette]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.type == "bg":
        _run_bg(args, w, h, rng, pal, out)
    elif args.type == "sprite":
        _run_sprite(args, w, h, pal, out)
    elif args.type == "face":
        _run_face(args, w, h, pal, out)


def _run_bg(args, w, h, rng, pal, out):
    """bg 类型：Bayer 抖动占位背景 + --input 真实照片处理。"""
    if args.input:
        indir = Path(args.input)
        if not indir.is_dir():
            print(f"error: --input 目录不存在: {indir}", file=sys.stderr)
            sys.exit(1)
        exts = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
        files = [f for f in sorted(indir.iterdir()) if f.suffix.lower() in exts]
        if not files:
            print(f"error: {indir} 中无图片", file=sys.stderr)
            sys.exit(1)
        for f in files:
            gray = process_photo(f, w, h, rng)
            mask = bayer_dither(gray)
            arr = to_dualcolor(mask, pal["dark"], pal["light"])
            dest = out / (f.stem + ".png")
            save_png(arr, dest)
            print(f"ok  {dest}")
        return

    for name, gen in SCENES.items():
        gray = gen(w, h, rng)
        mask = bayer_dither(gray)
        arr = to_dualcolor(mask, pal["dark"], pal["light"])
        dest = out / (name + ".png")
        save_png(arr, dest)
        print(f"ok  {dest}  (palette={args.palette}, seed={args.seed})")


def _run_sprite(args, w, h, pal, out):
    """sprite 类型：黑色剪影 + 亮色描边、透明底。"""
    if args.input:
        print("error: --input 仅支持 --type bg", file=sys.stderr)
        sys.exit(1)
    img = gen_sprite(w, h, pal)
    dest = out / "sprite_placeholder.png"
    img.save(str(dest))
    print(f"ok  {dest}  (palette={args.palette}, {w}x{h})")


def _run_face(args, w, h, pal, out):
    """face 类型：方黑底 + 双层框 + 居中首字。"""
    if args.input:
        print("error: --input 仅支持 --type bg", file=sys.stderr)
        sys.exit(1)
    img = gen_face(w, h, pal, args.name)
    dest = out / (f"face_{args.name.lower()}.png")
    img.save(str(dest))
    print(f"ok  {dest}  (palette={args.palette}, name={args.name})")


if __name__ == "__main__":
    main()
