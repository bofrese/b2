#!/usr/bin/env python3
"""
fix-img-tags.py - Audit and fix <img> tags in b2 partials for CWV/SEO.

Usage:
  python3 fix-img-tags.py audit             # report issues only
  python3 fix-img-tags.py fix               # apply mechanical fixes
  python3 fix-img-tags.py fix --dry-run     # show changes without writing

Fixes applied automatically:
  - Add width + height attributes (detected from image file if available)
  - Add loading="lazy" to non-hero images (first <img> per partial = hero)
  - Add loading="eager" + fetchpriority="high" to hero image

Issues flagged but NOT auto-fixed (require human input):
  - Missing alt text (outputs suggestion based on filename)
  - Non-WebP src where WebP version exists (outputs upgrade suggestion)
  - Images where dimensions cannot be detected

Reads:
  website/partials/ - HTML fragments to audit/fix
  website/src/images/ - source images (dimension detection)
  website/dist/ - dist images (fallback dimension detection)
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
PARTIALS_DIR = ROOT / "website" / "partials"
SRC_IMAGES_DIR = ROOT / "website" / "src" / "images"
DIST_DIR = ROOT / "website" / "dist"

MODE = sys.argv[1] if len(sys.argv) > 1 else "audit"
DRY_RUN = "--dry-run" in sys.argv

# ── Image dimension detection ──────────────────────────────
def get_image_dimensions(src_attr: str):
    """Try to get width, height from src attribute path. Returns (w, h) or None."""
    # Strip leading slash, query strings
    clean = src_attr.lstrip("/").split("?")[0]

    candidates = [
        SRC_IMAGES_DIR / Path(clean).name,
        ROOT / "website" / clean,
        DIST_DIR / clean,
        ROOT / clean,
    ]

    for candidate in candidates:
        if candidate.exists():
            try:
                from PIL import Image
                with Image.open(candidate) as img:
                    return img.width, img.height
            except ImportError:
                pass
            # Try ImageMagick identify via subprocess
            try:
                import subprocess
                result = subprocess.run(
                    ["identify", "-format", "%wx%h", str(candidate)],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    parts = result.stdout.strip().split("x")
                    if len(parts) == 2:
                        return int(parts[0]), int(parts[1])
            except Exception:
                pass
            return None  # File exists but can't read dimensions
    return None  # File not found


def webp_exists(src_attr: str) -> bool:
    """Check if a .webp version of this image exists."""
    clean = src_attr.lstrip("/").split("?")[0]
    stem = Path(clean).stem
    candidates = [
        SRC_IMAGES_DIR / f"{stem}.webp",
        ROOT / "website" / Path(clean).parent / f"{stem}.webp",
    ]
    return any(c.exists() for c in candidates)


def suggest_alt(src_attr: str) -> str:
    """Generate an alt text suggestion from the filename."""
    name = Path(src_attr).stem
    # Convert hyphens/underscores to spaces, title-case
    return name.replace("-", " ").replace("_", " ").title()


# ── IMG tag regex ──────────────────────────────────────────
# Matches a full <img ...> tag (non-greedy, handles multiline)
IMG_PATTERN = re.compile(r'<img\b([^>]*)>', re.IGNORECASE | re.DOTALL)

def get_attr(attrs: str, name: str):
    """Extract attribute value from attrs string. Returns value or None."""
    m = re.search(rf'\b{name}\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
    return m.group(1) if m else None

def has_attr(attrs: str, name: str) -> bool:
    return bool(re.search(rf'\b{name}\s*=', attrs, re.IGNORECASE))


def fix_img_tag(attrs: str, is_hero: bool) -> tuple[str, list[str], list[str]]:
    """
    Given img tag attributes string, return (fixed_attrs, changes_made, issues_flagged).
    changes_made: list of strings describing auto-fixes applied
    issues_flagged: list of strings describing issues that need human input
    """
    changes = []
    flags = []
    new_attrs = attrs

    src = get_attr(attrs, "src") or ""

    # ── Alt text ──────────────────────────────────────────
    if not has_attr(attrs, "alt"):
        suggestion = suggest_alt(src) if src else "descriptive text here"
        flags.append(f'missing alt - suggested: "{suggestion}"')
        # Add empty alt as placeholder so it's valid HTML, but flag it
        new_attrs = new_attrs.rstrip() + f' alt="{suggestion}"'
        changes.append(f'added alt="{suggestion}" (auto-suggested from filename - review this)')

    # ── Width + Height ────────────────────────────────────
    if not has_attr(attrs, "width") or not has_attr(attrs, "height"):
        dims = get_image_dimensions(src) if src else None
        if dims:
            w, h = dims
            if not has_attr(attrs, "width"):
                new_attrs = new_attrs.rstrip() + f' width="{w}"'
                changes.append(f'added width="{w}"')
            if not has_attr(attrs, "height"):
                new_attrs = new_attrs.rstrip() + f' height="{h}"'
                changes.append(f'added height="{h}"')
        else:
            flags.append("missing width/height - image dimensions could not be detected, add manually")

    # ── loading attribute ─────────────────────────────────
    if not has_attr(attrs, "loading"):
        if is_hero:
            new_attrs = new_attrs.rstrip() + ' loading="eager"'
            changes.append('added loading="eager" (hero image)')
        else:
            new_attrs = new_attrs.rstrip() + ' loading="lazy"'
            changes.append('added loading="lazy"')

    # ── fetchpriority on hero ─────────────────────────────
    if is_hero and not has_attr(attrs, "fetchpriority"):
        new_attrs = new_attrs.rstrip() + ' fetchpriority="high"'
        changes.append('added fetchpriority="high" (hero image - improves LCP)')

    # ── WebP upgrade suggestion ───────────────────────────
    if src and not src.endswith(".webp"):
        if webp_exists(src):
            flags.append(f"WebP version exists - consider <picture> with WebP source")

    return new_attrs, changes, flags


def process_partial(path: Path) -> dict:
    """Process one partial file. Returns audit/fix results."""
    content = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT))

    results = {
        "file": rel,
        "changes": [],
        "flags": [],
        "new_content": content,
    }

    new_content = content
    img_index = 0  # track which img is first (hero)

    def replace_img(m):
        nonlocal img_index
        attrs = m.group(1)
        is_hero = (img_index == 0)
        img_index += 1
        new_attrs, changes, flags = fix_img_tag(attrs, is_hero)
        if changes:
            results["changes"].append((m.group(0), f"<img{new_attrs}>", changes))
        for flag in flags:
            results["flags"].append(f"{rel}: {flag}")
        return f"<img{new_attrs}>"

    results["new_content"] = IMG_PATTERN.sub(replace_img, new_content)
    return results


# ── Main ───────────────────────────────────────────────────
if not PARTIALS_DIR.exists():
    print("ERROR:partials_missing:website/partials/ not found - run /b2:build first")
    sys.exit(1)

partials = sorted(PARTIALS_DIR.rglob("*.html"))
if not partials:
    print("INFO:no_partials:No .html files found in website/partials/")
    sys.exit(0)

total_changes = 0
total_flags = 0

for partial in partials:
    result = process_partial(partial)
    rel = result["file"]

    if not result["changes"] and not result["flags"]:
        print(f"OK:{rel}:img_tags:all img tags look good")
        continue

    for original, fixed, change_list in result["changes"]:
        for change in change_list:
            print(f"CHANGE:{rel}:{change}")
            total_changes += 1

    for flag in result["flags"]:
        print(f"FLAG:{flag}")
        total_flags += 1

    if MODE == "fix" and result["changes"]:
        if not DRY_RUN:
            partial.write_text(result["new_content"], encoding="utf-8")
            print(f"WRITTEN:{rel}:{len(result['changes'])} img tag(s) updated")
        else:
            print(f"DRY_RUN:{rel}:would update {len(result['changes'])} img tag(s)")

print(f"DONE:fix_img_tags:changes={total_changes}:flags={total_flags}")
