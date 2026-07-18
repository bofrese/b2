#!/usr/bin/env python3
"""
prep-images.py — Resize, compress, and convert images for web production.

What this does:
  1. Resize  — shrink to --max-width if larger (preserving aspect ratio)
  2. Compress fallback — re-save the JPEG/PNG at web quality (removes bloat,
     EXIF data, and embedded colour profiles). The fallback is what browsers
     that don't support WebP receive, and what crawlers/bots often fetch.
  3. Convert — create a .webp alongside the optimised fallback for modern browsers.

The <picture> pattern in HTML then serves WebP to 97%+ of users and the
optimised JPEG/PNG to the rest. Both files are small.

USAGE
  Audit (no changes, shows what would happen):
    python3 prep-images.py website/src/images/

  Process all images in a directory:
    python3 prep-images.py website/src/images/ --fix

  Process a single image:
    python3 prep-images.py website/src/images/hero.jpg --fix

  Hero images (large, full-bleed):
    python3 prep-images.py website/src/images/hero.jpg --fix --max-width 1920

  Content images (in-page, not full-bleed):
    python3 prep-images.py website/src/images/team.jpg --fix --max-width 1200

  Thumbnails / card images:
    python3 prep-images.py website/src/images/card.jpg --fix --max-width 800

  After layout change — reconvert everything at new quality:
    python3 prep-images.py website/src/images/ --fix --force

OPTIONS
  --fix                Apply changes. Default: audit only (no files written).
  --max-width N        Resize if image is wider than N px (default: 1920).
  --webp-quality N     WebP quality 1–100 (default: 82). 82 is near-lossless.
  --jpg-quality N      JPEG fallback quality 1–100 (default: 85).
  --force              Reprocess even if output files already exist.
  --delete-originals   Remove the oversized source file after processing.
                       Use only when originals are safely in git or a backup.

OUTPUT FORMAT (structured lines — parsed by the seo-expert skill)
  TOOL:available:pillow=true:imagemagick=true:cwebp=true
  WOULD_FIX:path:WxH:NKB:actions
  RESIZE:path:3200x2000 → 1920x1200
  COMPRESS:path:hero.jpg:340KB → 95KB (saved 245KB)
  CONVERT:path:hero.jpg → hero.webp:340KB → 52KB (saved 288KB)
  SKIP:path:reason
  OK:path:status:WxH:NKB
  WARN:path:message
  ERROR:path:message
  DONE:summary:processed=N:skipped=N:errors=N:saved=NKB

REQUIREMENTS
  Pillow (preferred):  pip install Pillow
  Fallback options:    brew install webp   (cwebp)
                       brew install imagemagick
  Pillow is strongly recommended — it handles fallback compression and is
  more reliable than shell tool combinations.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ── Argument parsing ───────────────────────────────────────────────
args = sys.argv[1:]

TARGET = None
FIX_MODE       = "--fix" in args
DELETE_ORIGINALS = "--delete-originals" in args
FORCE          = "--force" in args

MAX_WIDTH    = 1920
WEBP_QUALITY = 82
JPG_QUALITY  = 85  # for the fallback JPEG

i = 0
while i < len(args):
    a = args[i]
    if a == "--max-width"    and i + 1 < len(args): MAX_WIDTH    = int(args[i+1]); i += 2; continue
    if a == "--webp-quality" and i + 1 < len(args): WEBP_QUALITY = int(args[i+1]); i += 2; continue
    if a == "--jpg-quality"  and i + 1 < len(args): JPG_QUALITY  = int(args[i+1]); i += 2; continue
    if not a.startswith("--"): TARGET = Path(a)
    i += 1

if TARGET is None:
    print("ERROR:args:Usage: python3 prep-images.py <path|directory> [--fix] [options]")
    sys.exit(1)

# ── Tool detection ─────────────────────────────────────────────────
HAS_PILLOW       = False
HAS_IMAGEMAGICK  = False
HAS_CWEBP        = False

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    pass

def _cmd(name):
    try:
        subprocess.run([name, "--version"], capture_output=True, timeout=3)
        return True
    except Exception:
        return False

HAS_IMAGEMAGICK = _cmd("convert") and _cmd("identify")
HAS_CWEBP       = _cmd("cwebp")

print(f"TOOL:available:pillow={str(HAS_PILLOW).lower()}:imagemagick={str(HAS_IMAGEMAGICK).lower()}:cwebp={str(HAS_CWEBP).lower()}")

if not HAS_PILLOW and not HAS_IMAGEMAGICK and not HAS_CWEBP:
    print("ERROR:tools:No image processing tools found.")
    print("INFO:install:pip install Pillow          (recommended)")
    print("INFO:install:brew install webp            (cwebp)")
    print("INFO:install:brew install imagemagick     (convert/identify)")
    sys.exit(1)

if not HAS_PILLOW:
    print("WARN:tools:Pillow not found — fallback JPEG/PNG compression unavailable.")
    print("INFO:tools:Install Pillow for best results: pip install Pillow")

# ── File collection ────────────────────────────────────────────────
SOURCE_EXTS = {".jpg", ".jpeg", ".png"}
ALL_EXTS    = SOURCE_EXTS | {".webp", ".gif"}

if TARGET.is_dir():
    images = sorted(p for p in TARGET.rglob("*") if p.suffix.lower() in ALL_EXTS)
elif TARGET.is_file():
    images = [TARGET]
else:
    print(f"ERROR:path:{TARGET} does not exist")
    sys.exit(1)

if not images:
    print(f"INFO:scan:No images found in {TARGET}")
    sys.exit(0)

# ── Helpers ────────────────────────────────────────────────────────
def kb(path):
    return os.path.getsize(path) // 1024

def get_dims(path):
    if HAS_PILLOW:
        try:
            with Image.open(path) as img:
                return img.size  # (w, h)
        except Exception:
            pass
    if HAS_IMAGEMAGICK:
        try:
            r = subprocess.run(["identify", "-format", "%wx%h", str(path)],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                w, h = r.stdout.strip().split("x")
                return int(w), int(h)
        except Exception:
            pass
    return None

def dims_str(dims):
    return f"{dims[0]}x{dims[1]}" if dims else "?"

# ── Pillow-based processing (primary path) ─────────────────────────
def process_with_pillow(src_path, max_width, webp_quality, jpg_quality):
    """
    Resize + compress fallback + convert to WebP using Pillow.
    Returns dict with keys: resized, fallback_saved_kb, webp_kb, orig_kb, final_dims
    """
    with Image.open(src_path) as img:
        orig_w, orig_h = img.size
        orig_mode = img.mode

        # Determine output format for fallback
        ext = src_path.suffix.lower()
        is_png = ext == ".png"

        # Resize if needed
        resized = False
        if orig_w > max_width:
            new_w = max_width
            new_h = int(orig_h * max_width / orig_w)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            resized = True
        else:
            new_w, new_h = orig_w, orig_h

        # Keep alpha for PNG if present; convert others to RGB
        if is_png and orig_mode in ("RGBA", "LA", "P"):
            save_img = img.convert("RGBA")
        else:
            save_img = img.convert("RGB")

        # ── Compress fallback (overwrite original with optimised version) ──
        orig_kb = kb(src_path)
        fallback_path = src_path  # overwrite in place

        if is_png:
            # PNG: lossless re-save strips EXIF, comments, metadata.
            # For large size reduction, convert to JPEG unless transparency needed.
            save_img.save(fallback_path, "PNG", optimize=True)
        else:
            # JPEG: re-save at web quality strips EXIF and reduces bloat significantly.
            save_img.save(fallback_path, "JPEG", quality=jpg_quality, optimize=True, progressive=True)

        new_fallback_kb = kb(fallback_path)

        # ── Convert to WebP ────────────────────────────────────────────────
        webp_path = src_path.with_suffix(".webp")
        if save_img.mode == "RGBA":
            save_img.save(webp_path, "WEBP", quality=webp_quality, lossless=False)
        else:
            save_img.convert("RGB").save(webp_path, "WEBP", quality=webp_quality, method=6)

        webp_kb_val = kb(webp_path)

        return {
            "resized":          resized,
            "orig_dims":        (orig_w, orig_h),
            "final_dims":       (new_w, new_h),
            "orig_kb":          orig_kb,
            "fallback_kb":      new_fallback_kb,
            "webp_kb":          webp_kb_val,
            "webp_path":        webp_path,
        }

# ── Shell fallback (no Pillow — WebP only, no fallback compression) ─
def process_with_shell(src_path, max_width, webp_quality):
    orig_kb_val = kb(src_path)
    dims = get_dims(src_path)
    resized = False
    work = src_path

    # Resize with ImageMagick if needed
    if dims and dims[0] > max_width and HAS_IMAGEMAGICK:
        tmp = src_path.parent / f"_resized_{src_path.name}"
        r = subprocess.run(
            ["convert", str(src_path), "-resize", f"{max_width}>", str(tmp)],
            capture_output=True, timeout=30
        )
        if r.returncode == 0:
            work = tmp
            dims = get_dims(tmp)
            resized = True

    webp_path = src_path.with_suffix(".webp")
    ok = False

    if HAS_CWEBP:
        r = subprocess.run(
            ["cwebp", "-q", str(webp_quality), str(work), "-o", str(webp_path)],
            capture_output=True, timeout=60
        )
        ok = r.returncode == 0
    elif HAS_IMAGEMAGICK:
        r = subprocess.run(
            ["convert", str(work), "-quality", str(webp_quality), str(webp_path)],
            capture_output=True, timeout=60
        )
        ok = r.returncode == 0

    if work != src_path and work.exists():
        work.unlink()

    return {
        "ok":        ok,
        "resized":   resized,
        "orig_dims": dims,
        "orig_kb":   orig_kb_val,
        "webp_path": webp_path if ok else None,
        "webp_kb":   kb(webp_path) if ok and webp_path.exists() else 0,
    }

# ── Main processing loop ───────────────────────────────────────────
total_saved_kb = 0
processed = skipped = errors = 0

for img_path in images:
    rel  = str(img_path)
    ext  = img_path.suffix.lower()
    webp_path = img_path.with_suffix(".webp")

    # ── Already WebP ──────────────────────────────────────────────
    if ext == ".webp":
        dims = get_dims(img_path)
        if dims and dims[0] > MAX_WIDTH:
            print(f"WARN:{rel}:webp is {dims[0]}px wide (>{MAX_WIDTH}px) — regenerate from source with --force")
        else:
            print(f"OK:{rel}:webp:{dims_str(dims)}:{kb(img_path)}KB")
        skipped += 1
        continue

    # ── Skip non-source files ─────────────────────────────────────
    if ext not in SOURCE_EXTS:
        skipped += 1
        continue

    # ── Check if already processed ────────────────────────────────
    src_kb   = kb(img_path)
    dims     = get_dims(img_path)
    needs_resize = dims and dims[0] > MAX_WIDTH

    if webp_path.exists() and not FORCE:
        webp_kb_val = kb(webp_path)
        print(f"SKIP:{rel}:already processed:{dims_str(dims)}:src={src_kb}KB:webp={webp_kb_val}KB (--force to redo)")
        skipped += 1
        continue

    # ── Audit mode — report what would happen ─────────────────────
    if not FIX_MODE:
        actions = []
        if needs_resize:
            actions.append(f"resize {dims[0]}→{MAX_WIDTH}px")
        if HAS_PILLOW:
            actions.append(f"compress fallback (JPEG q{JPG_QUALITY})")
        actions.append(f"convert to WebP (q{WEBP_QUALITY})")
        print(f"WOULD_FIX:{rel}:{dims_str(dims)}:{src_kb}KB — {', '.join(actions)}")
        continue

    # ── Fix mode ──────────────────────────────────────────────────
    try:
        if HAS_PILLOW:
            res = process_with_pillow(img_path, MAX_WIDTH, WEBP_QUALITY, JPG_QUALITY)

            if res["resized"]:
                od = res["orig_dims"]; fd = res["final_dims"]
                print(f"RESIZE:{rel}:{od[0]}x{od[1]} → {fd[0]}x{fd[1]}")

            fb_saved = res["orig_kb"] - res["fallback_kb"]
            if fb_saved > 0:
                print(f"COMPRESS:{rel}:{img_path.name}:{res['orig_kb']}KB → {res['fallback_kb']}KB (saved {fb_saved}KB)")

            total_kb_before = res["orig_kb"]
            webp_saved = res["orig_kb"] - res["webp_kb"]
            fd = res["final_dims"]
            print(f"CONVERT:{rel}:{img_path.name} → {res['webp_path'].name}:{res['orig_kb']}KB → {res['webp_kb']}KB (saved {webp_saved}KB) {fd[0]}x{fd[1]}")

            total_saved_kb += max(fb_saved, 0) + max(webp_saved, 0)

        else:
            # Shell fallback — WebP only, no fallback compression
            res = process_with_shell(img_path, MAX_WIDTH, WEBP_QUALITY)
            if not res["ok"]:
                print(f"ERROR:{rel}:conversion failed")
                errors += 1
                continue
            if res["resized"]:
                print(f"RESIZE:{rel}:{dims_str(res['orig_dims'])} → ≤{MAX_WIDTH}px")
            webp_saved = res["orig_kb"] - res["webp_kb"]
            print(f"CONVERT:{rel}:{img_path.name} → {res['webp_path'].name}:{res['orig_kb']}KB → {res['webp_kb']}KB (saved {webp_saved}KB)")
            total_saved_kb += max(webp_saved, 0)

        if DELETE_ORIGINALS:
            img_path.unlink()
            print(f"DELETED:{rel}:original removed")

        processed += 1

    except Exception as e:
        print(f"ERROR:{rel}:{e}")
        errors += 1

# ── Summary ────────────────────────────────────────────────────────
if FIX_MODE:
    print(f"DONE:summary:processed={processed}:skipped={skipped}:errors={errors}:saved={total_saved_kb}KB")
else:
    print(f"DONE:audit:images={len(images)}:skipped={skipped}:run with --fix to apply changes")
