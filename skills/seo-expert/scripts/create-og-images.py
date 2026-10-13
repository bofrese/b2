#!/usr/bin/env python3
"""
create-og-images.py - Auto-generate 1200x630 og:image crops for every page.

For each partial in website/partials/, finds the first <img src="..."> that references
a real image file, then creates a 1200x630 center-crop WebP in website/dist/images/.

Naming: {slug}-og-image.webp
  - about.html            → about-og-image.webp
  - articles/foo.html     → foo-og-image.webp
  - ai/index.html         → ai-og-image.webp

Usage:
  python3 create-og-images.py audit           # show what would be created, no writes
  python3 create-og-images.py fix             # create og:images
  python3 create-og-images.py fix --force     # overwrite existing

Output format (one line per page):
  WOULD_CREATE:{slug}:{source_img}:{output_path}   (audit mode)
  CREATED:{slug}:{source_img}:{output_path}         (fix mode)
  SKIP:{slug}:no_source_image                       (no usable image found)
  SKIP:{slug}:already_exists:{output_path}          (exists, no --force)
  DONE:summary:N created:M skipped
"""

import re, sys, os, glob

OG_W, OG_H = 1200, 630
DIST_IMAGES = "website/dist/images"
PARTIALS_DIR = "website/partials"

# Image extensions to skip (not page illustrations)
SKIP_EXTS = {".svg"}
# Path fragments that indicate a logo/icon, not a page image
SKIP_PATTERNS = ["logo", "favicon", "icon", "avatar"]


def center_crop(img, w, h):
    from PIL import Image
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    if scale != 1.0:
        img = img.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
        iw, ih = img.size
    left = (iw - w) // 2
    top = (ih - h) // 2
    return img.crop((left, top, left + w, top + h))


def save_webp(img, path, quality=85):
    rgb = img.convert("RGB") if img.mode != "RGB" else img
    rgb.save(path, "WebP", quality=quality, method=6)


def slug_for_partial(rel_path):
    """
    about.html             → about
    articles/foo.html      → foo
    articles/index.html    → articles
    ai/index.html          → ai
    ai/agentic-dev.html    → agentic-dev
    """
    base = rel_path.replace(".html", "")
    parts = base.split("/")
    if parts[-1] == "index":
        return parts[-2] if len(parts) > 1 else "index"
    return parts[-1]


def find_first_image(partial_path):
    """Return the first img src that looks like a real page illustration."""
    with open(partial_path) as f:
        content = f.read()
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE):
        src = m.group(1)
        ext = os.path.splitext(src)[1].lower()
        if ext in SKIP_EXTS:
            continue
        if any(p in src.lower() for p in SKIP_PATTERNS):
            continue
        return src
    return None


def resolve_image_path(src):
    """
    Resolve an img src to a real file path.
    Tries dist/images/ first, then src/images/.
    """
    filename = os.path.basename(src)
    candidates = [
        os.path.join(DIST_IMAGES, filename),
        os.path.join("website/src/images", filename),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def main():
    mode = "audit"
    force = False
    for arg in sys.argv[1:]:
        if arg == "fix":
            mode = "fix"
        elif arg == "audit":
            mode = "audit"
        elif arg == "--force":
            force = True

    try:
        from PIL import Image
        pillow_ok = True
    except ImportError:
        pillow_ok = False
        if mode == "fix":
            print("ERROR: Pillow not installed. Run: pip install Pillow")
            sys.exit(1)

    os.makedirs(DIST_IMAGES, exist_ok=True)

    partials = sorted(
        glob.glob(f"{PARTIALS_DIR}/**/*.html", recursive=True) +
        glob.glob(f"{PARTIALS_DIR}/*.html")
    )

    created = 0
    skipped = 0

    seen_slugs = set()
    for partial_path in partials:
        rel = partial_path[len(PARTIALS_DIR) + 1:]
        slug = slug_for_partial(rel)
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        output_name = f"{slug}-og-image.webp"
        output_path = os.path.join(DIST_IMAGES, output_name)

        src = find_first_image(partial_path)
        if not src:
            print(f"SKIP:{slug}:no_source_image")
            skipped += 1
            continue

        real_path = resolve_image_path(src)
        if not real_path:
            print(f"SKIP:{slug}:image_file_not_found:{src}")
            skipped += 1
            continue

        if os.path.exists(output_path) and not force:
            print(f"SKIP:{slug}:already_exists:{output_path}")
            skipped += 1
            continue

        rel_output = f"/images/{output_name}"

        if mode == "audit":
            print(f"WOULD_CREATE:{slug}:{real_path}:{output_path}:{rel_output}")
        else:
            try:
                from PIL import Image
                img = Image.open(real_path)
                img = center_crop(img, OG_W, OG_H)
                save_webp(img, output_path)
                kb = os.path.getsize(output_path) // 1024
                print(f"CREATED:{slug}:{real_path}:{output_path}:{rel_output}:{kb}KB")
                created += 1
            except Exception as e:
                print(f"ERROR:{slug}:{e}")
                skipped += 1

    if mode == "audit":
        print(f"DONE:audit:{len(seen_slugs)} pages checked")
    else:
        print(f"DONE:summary:{created} created:{skipped} skipped")


if __name__ == "__main__":
    main()
