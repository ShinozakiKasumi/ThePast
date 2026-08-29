#!/usr/bin/env python3
"""Extract Noto Sans Mono CJK SC/TC from the system .ttc and copy IBM Plex Mono.

One-time dev utility: the system ships NotoSansCJK-*.ttc (a TrueType Collection
holding many faces) and IBM Plex Mono. Ren'Py loads face 0 of a .ttc by default,
which is *not* the Mono CJK variant we want, so we extract the right face into a
standalone OTF and drop it in game/fonts/.

Extracts both SC (Simplified Chinese) and TC (Traditional Chinese) faces.
The game uses TC as the base language; SC is kept for fallback.

Re-run anytime; overwrites in place. Fails soft: prints a TODO and exits 0 so a
missing font never breaks the build pipeline.

Usage:
    python3 tools/setup_fonts.py [--src NOTO_DIR] [--plex PLEX_DIR] [--out OUT]
"""
import argparse
import shutil
import sys
from pathlib import Path

try:
    from fontTools.ttLib import TTCollection, TTFont
except ImportError:
    print("TODO: fonttools not installed; run `pip install fonttools`.")
    sys.exit(0)


def find_mono_cjk_face(ttc_path, lang="SC"):
    """Return the TTFont whose family name is 'Noto Sans Mono CJK <lang>'."""
    ttc = TTCollection(ttc_path)
    for font in ttc.fonts:
        name = font["name"].getDebugName(1)  # family name
        if name and f"Mono CJK {lang}" in name:
            return font
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/usr/share/fonts/opentype/noto",
                    help="dir holding NotoSansCJK-*.ttc")
    ap.add_argument("--plex", default="/usr/share/fonts/truetype/ibm-plex",
                    help="dir holding IBMPlexMono-*.ttf")
    ap.add_argument("--out", default="game/fonts",
                    help="output directory")
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # --- Noto Sans Mono CJK SC + TC (Regular + Bold) ---
    targets = [
        (src / "NotoSansCJK-Regular.ttc", "NotoSansMonoCJKsc-Regular.otf", "SC"),
        (src / "NotoSansCJK-Bold.ttc",    "NotoSansMonoCJKsc-Bold.otf",    "SC"),
        (src / "NotoSansCJK-Regular.ttc", "NotoSansMonoCJKtc-Regular.otf", "TC"),
        (src / "NotoSansCJK-Bold.ttc",    "NotoSansMonoCJKtc-Bold.otf",    "TC"),
    ]
    for ttc_path, out_name, lang in targets:
        if not ttc_path.exists():
            print(f"TODO: {ttc_path} not found; skip {out_name}")
            continue
        face = find_mono_cjk_face(ttc_path, lang)
        if face is None:
            print(f"TODO: 'Noto Sans Mono CJK {lang}' face not found in {ttc_path}")
            continue
        dest = out / out_name
        face.save(str(dest))
        print(f"ok  {dest}  ({dest.stat().st_size // 1024} KiB)")

    # --- IBM Plex Mono (Regular + Bold) ---
    plex = Path(args.plex)
    for name in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Bold.ttf"):
        p = plex / name
        if not p.exists():
            print(f"TODO: {p} not found; skip")
            continue
        dest = out / name
        shutil.copyfile(p, dest)
        print(f"ok  {dest}  ({dest.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
