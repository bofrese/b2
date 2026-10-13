#!/usr/bin/env python3
"""
generate-favicon.py - Generate a full favicon set from the site's own brand
mark, so the browser tab/bookmark/home-screen icon matches the nav logo
exactly rather than being a separate, uncoordinated asset.

Two ways to source the mark (the caller decides which fits the theme - this
script does not guess, since brand-mark markup varies too much to detect
reliably across arbitrary themes):

  1. An existing square-ish logo image:
       --image path/to/logo.png

  2. A CSS text badge (the common b2 pattern: a rounded-corner color chip with
     bold text, e.g. a `.brandmark` class - background color + text + font +
     corner radius, all already defined in the theme's header.html/styles.css):
       --text "B2" --bg "#E8531D" [--fg "#FFFFFF"] [--font path/to/font.ttf] [--radius 28]

     --radius is a percentage of the icon size (28 matches a typical
     ~12px-radius-on-40px chip). --font accepts .ttf/.otf; if omitted, falls
     back to a system sans-serif bold (Arial/Helvetica) since a self-hosted
     display font may not exist yet at design time - using the wrong font at
     favicon size is a much smaller problem than blocking on font setup.

Output: favicon.ico (16/32/48 bundled) + favicon-16.png + favicon-32.png +
favicon-192.png + apple-touch-icon.png (180x180), written to the given
--out-dir (default: website/src/assets/), with favicon.ico placed at
website/src/favicon.ico (browsers probe that path by convention regardless
of <link> tags).

Usage:
  python3 generate-favicon.py --image website/theme/b2/assets/logo.png
  python3 generate-favicon.py --text "B2" --bg "#E8531D" --font /path/to/ClashDisplay-Bold.ttf

Output format:
  WRITTEN:{path}
  DONE:favicon:{n} files written
"""

import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR:pillow_missing:pip install Pillow")
    sys.exit(1)

SIZES = [16, 32, 48, 180, 192, 512]
FALLBACK_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def find_fallback_font():
    for path in FALLBACK_FONTS:
        if os.path.exists(path):
            return path
    return None


def make_text_icon(size, text, bg, fg, font_path, radius_pct):
    scale = 4  # supersample for crisp corners/text, then downscale
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = int(s * radius_pct / 100)
    draw.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=bg)

    font = ImageFont.truetype(font_path, int(s * 0.52))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (s - tw) / 2 - bbox[0]
    y = (s - th) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fg)

    return img.resize((size, size), Image.LANCZOS)


def make_image_icon(size, source_path):
    im = Image.open(source_path).convert("RGBA")
    w, h = im.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    return im.resize((size, size), Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", help="Existing logo image to crop/resize")
    parser.add_argument("--text", help="Text to render on a color chip (e.g. site initials)")
    parser.add_argument("--bg", default="#000000", help="Chip background color (hex)")
    parser.add_argument("--fg", default="#FFFFFF", help="Text color (hex)")
    parser.add_argument("--font", help="Path to a .ttf/.otf font file (bold recommended)")
    parser.add_argument("--radius", type=float, default=25, help="Corner radius as %% of icon size")
    parser.add_argument("--out-dir", default="website/src/assets")
    parser.add_argument("--favicon-ico-path", default="website/src/favicon.ico")
    args = parser.parse_args()

    if not args.image and not args.text:
        print("ERROR:no_source:pass --image <path> or --text <string> (with --bg)")
        sys.exit(1)

    if args.text:
        font_path = args.font or find_fallback_font()
        if not font_path:
            print("ERROR:no_font:pass --font <path> - no system fallback font found")
            sys.exit(1)
        bg = hex_to_rgb(args.bg)
        fg = hex_to_rgb(args.fg)

    os.makedirs(args.out_dir, exist_ok=True)
    written = []

    icons = {}
    for size in SIZES:
        if args.image:
            icons[size] = make_image_icon(size, args.image)
        else:
            icons[size] = make_text_icon(size, args.text, bg, fg, font_path, args.radius)

    name_map = {16: "favicon-16.png", 32: "favicon-32.png", 192: "favicon-192.png", 512: "favicon-512.png"}
    for size, fname in name_map.items():
        path = os.path.join(args.out_dir, fname)
        icons[size].save(path)
        written.append(path)

    apple_path = os.path.join(args.out_dir, "apple-touch-icon.png")
    icons[180].save(apple_path)
    written.append(apple_path)

    # Use the 48px instance as the source so .ico's smaller sizes are downscaled,
    # never upscaled from a smaller source (which would look blurry).
    icons[48].save(args.favicon_ico_path, sizes=[(16, 16), (32, 32), (48, 48)])
    written.append(args.favicon_ico_path)

    for path in written:
        print(f"WRITTEN:{path}")
    print(f"DONE:favicon:{len(written)} files written")


if __name__ == "__main__":
    main()
