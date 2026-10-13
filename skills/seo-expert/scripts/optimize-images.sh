#!/usr/bin/env bash
# optimize-images.sh - Audit and convert images for b2 SEO / performance
#
# Usage:
#   bash optimize-images.sh audit - report only, no changes
#   bash optimize-images.sh convert - convert JPG/PNG → WebP (src/images only)
#   bash optimize-images.sh convert --force - reconvert even if WebP already exists
#
# Reads:  website/src/images/  (source images to optimise)
#         website/partials/     (check img tags for width/height/alt/lazy)
#         website/dist/         (check what's actually served)
# Writes: website/src/images/*.webp  (on 'convert' mode)
#
# Requires one of: cwebp, ImageMagick (convert+identify), ffmpeg, Python+Pillow

set -uo pipefail

ROOT="$(pwd)"
SRC_IMG="$ROOT/website/src/images"
DIST_IMG="$ROOT/website/dist"
MODE="${1:-audit}"
FORCE="${2:-}"

# ────────────────────────────────────────────────────────────
# Tool detection
# ────────────────────────────────────────────────────────────
HAS_CWEBP=false
HAS_IMAGEMAGICK=false
HAS_FFMPEG=false
HAS_PYTHON_PILLOW=false
HAS_IDENTIFY=false
TOOL_AVAIL=false

detect_tools() {
  command -v cwebp >/dev/null 2>&1 && HAS_CWEBP=true
  if command -v identify >/dev/null 2>&1; then HAS_IDENTIFY=true; fi
  if command -v convert >/dev/null 2>&1 && command -v identify >/dev/null 2>&1; then HAS_IMAGEMAGICK=true; fi
  command -v ffmpeg >/dev/null 2>&1 && HAS_FFMPEG=true
  python3 -c "from PIL import Image" 2>/dev/null && HAS_PYTHON_PILLOW=true

  echo "TOOLS:cwebp=$HAS_CWEBP:imagemagick=$HAS_IMAGEMAGICK:ffmpeg=$HAS_FFMPEG:pillow=$HAS_PYTHON_PILLOW"

  if $HAS_CWEBP || $HAS_IMAGEMAGICK || $HAS_FFMPEG || $HAS_PYTHON_PILLOW; then
    TOOL_AVAIL=true
    echo "TOOL_AVAIL:true"
  else
    echo "WARN:tools:none_found:No image conversion tools detected."
    echo "INFO:tools:install_options:Install one of: cwebp (brew install webp), ImageMagick (brew install imagemagick), Python Pillow (pip install Pillow)"
    echo "TOOL_AVAIL:false"
  fi
}

# ────────────────────────────────────────────────────────────
# Get image dimensions (WxH)
# ────────────────────────────────────────────────────────────
get_dimensions() {
  local FILE="$1"
  if $HAS_IDENTIFY; then
    identify -format "%wx%h" "$FILE" 2>/dev/null || echo "unknown"
  elif $HAS_PYTHON_PILLOW; then
    python3 -c "
from PIL import Image
try:
    with Image.open('$FILE') as img:
        print(f'{img.width}x{img.height}')
except:
    print('unknown')
" 2>/dev/null
  else
    echo "unknown"
  fi
}

# ────────────────────────────────────────────────────────────
# Get file size in KB
# ────────────────────────────────────────────────────────────
get_size_kb() {
  local FILE="$1"
  local BYTES
  BYTES=$(wc -c < "$FILE" 2>/dev/null | tr -d ' ')
  echo $(( BYTES / 1024 ))
}

# ────────────────────────────────────────────────────────────
# Convert one image to WebP
# ────────────────────────────────────────────────────────────
convert_to_webp() {
  local SRC="$1"
  local DST="$2"
  local QUALITY="${3:-82}"

  if $HAS_CWEBP; then
    cwebp -q "$QUALITY" "$SRC" -o "$DST" 2>/dev/null && echo "OK" && return
  fi
  if $HAS_IMAGEMAGICK; then
    convert "$SRC" -quality "$QUALITY" "$DST" 2>/dev/null && echo "OK" && return
  fi
  if $HAS_FFMPEG; then
    ffmpeg -i "$SRC" -q:v 85 "$DST" -y 2>/dev/null && echo "OK" && return
  fi
  if $HAS_PYTHON_PILLOW; then
    python3 -c "
from PIL import Image
img = Image.open('$SRC')
if img.mode in ('RGBA', 'LA'):
    img.save('$DST', 'WEBP', quality=$QUALITY, lossless=False)
else:
    img.convert('RGB').save('$DST', 'WEBP', quality=$QUALITY)
" 2>/dev/null && echo "OK" && return
  fi
  echo "FAIL"
}

# ────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────
detect_tools

# Source image audit
if [ -d "$SRC_IMG" ]; then
  SRC_FILES=$(find "$SRC_IMG" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.webp" \) 2>/dev/null | sort)
else
  echo "WARN:src:no_image_dir:website/src/images/ not found - no source images to audit"
  SRC_FILES=""
fi

# ── Per-image audit ────────────────────────────────────────
for IMG in $SRC_FILES; do
  REL="${IMG#$ROOT/}"
  EXT="${IMG##*.}"
  EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')
  SIZE_KB=$(get_size_kb "$IMG")
  DIMS=$(get_dimensions "$IMG")

  # Already WebP?
  if [ "$EXT_LOWER" = "webp" ]; then
    echo "OK:$REL:format:already WebP (${SIZE_KB}KB, ${DIMS})"
    continue
  fi

  # Check if WebP version exists
  WEBP_PATH="${IMG%.*}.webp"
  WEBP_EXISTS=false
  [ -f "$WEBP_PATH" ] && WEBP_EXISTS=true

  # Parse dimensions for size warnings
  WIDTH=$(echo "$DIMS" | cut -dx -f1 2>/dev/null || echo "0")
  HEIGHT=$(echo "$DIMS" | cut -dx -f2 2>/dev/null || echo "0")

  # Warn on large dimensions
  if [ "$WIDTH" != "unknown" ] && [ "$WIDTH" -gt 2400 ] 2>/dev/null; then
    echo "WARN:$REL:oversized:${DIMS}px - hero images rarely need more than 1920px wide"
  elif [ "$WIDTH" != "unknown" ] && [ "$WIDTH" -gt 1200 ] 2>/dev/null; then
    echo "INFO:$REL:large_dims:${DIMS}px - consider 1200px max for content images"
  fi

  # Warn on file size
  if [ "$SIZE_KB" -gt 300 ]; then
    echo "WARN:$REL:large_file:${SIZE_KB}KB - should be <150KB after WebP conversion"
  elif [ "$SIZE_KB" -gt 100 ]; then
    echo "INFO:$REL:file_size:${SIZE_KB}KB (acceptable, but WebP conversion will help)"
  fi

  if $WEBP_EXISTS; then
    WEBP_SIZE_KB=$(get_size_kb "$WEBP_PATH")
    echo "OK:$REL:webp_exists:${EXT_LOWER} ${SIZE_KB}KB → webp ${WEBP_SIZE_KB}KB already converted"
  else
    echo "ISSUE:$REL:not_webp:${EXT_LOWER} ${SIZE_KB}KB ${DIMS} - WebP version missing"
  fi

  # ── Convert mode ─────────────────────────────────────────
  if [ "$MODE" = "convert" ]; then
    if $WEBP_EXISTS && [ "$FORCE" != "--force" ]; then
      echo "SKIP:$REL:webp_exists:use --force to reconvert"
      continue
    fi

    if ! $TOOL_AVAIL; then
      echo "ERROR:$REL:no_tool:No conversion tool available - see TOOL_AVAIL line above"
      continue
    fi

    RESULT=$(convert_to_webp "$IMG" "$WEBP_PATH" 82)
    if [ "$RESULT" = "OK" ]; then
      NEW_SIZE_KB=$(get_size_kb "$WEBP_PATH")
      SAVING=$(( SIZE_KB - NEW_SIZE_KB ))
      echo "CONVERTED:$REL:webp:${SIZE_KB}KB → ${NEW_SIZE_KB}KB (saved ${SAVING}KB)"
    else
      echo "ERROR:$REL:convert_failed:Could not convert to WebP"
    fi
  fi
done

# ── Partial tag audit ─────────────────────────────────────
# Check img tags in partials for missing width, height, alt, loading
PARTIALS_DIR="$ROOT/website/partials"
if [ -d "$PARTIALS_DIR" ]; then
  for PARTIAL in $(find "$PARTIALS_DIR" -name "*.html" | sort); do
    REL="${PARTIAL#$ROOT/}"
    CONTENT=$(cat "$PARTIAL")

    # Images without width/height - use arithmetic: total minus those with attr
    IMG_TOTAL=$(echo "$CONTENT" | grep -c '<img ' || true)
    IMG_WITH_WIDTH=$(echo "$CONTENT" | grep -cE '<img [^>]*width=' || true)
    IMG_WITH_HEIGHT=$(echo "$CONTENT" | grep -cE '<img [^>]*height=' || true)
    IMG_NO_WIDTH=$(( IMG_TOTAL - IMG_WITH_WIDTH ))
    IMG_NO_HEIGHT=$(( IMG_TOTAL - IMG_WITH_HEIGHT ))
    IMG_NO_DIMS=$(( IMG_NO_WIDTH > IMG_NO_HEIGHT ? IMG_NO_WIDTH : IMG_NO_HEIGHT ))
    if [ "$IMG_NO_DIMS" -gt 0 ]; then
      echo "WARN:$REL:img_no_dimensions:${IMG_NO_DIMS} <img> tag(s) missing width/height - causes CLS"
    fi

    # Images without loading attribute
    IMG_WITH_LOADING=$(echo "$CONTENT" | grep -cE '<img [^>]*loading=' || true)
    IMG_NO_LAZY=$(( IMG_TOTAL - IMG_WITH_LOADING ))
    if [ "$IMG_NO_LAZY" -gt 0 ]; then
      echo "INFO:$REL:img_no_lazy:${IMG_NO_LAZY} <img> tag(s) without loading attribute - add loading=\"lazy\" for below-fold images"
    fi

    # Non-WebP src references
    NON_WEBP=$(echo "$CONTENT" | grep -cE 'src="[^"]+\.(png|jpg|jpeg|gif)"' || true)
    if [ "$NON_WEBP" -gt 0 ]; then
      echo "WARN:$REL:img_not_webp:${NON_WEBP} <img> src(s) referencing non-WebP files"
    fi
  done
fi

# ── Theme CSS performance check ────────────────────────────
CFG="$ROOT/website/b2.cfg"
THEME=$(grep '^THEME=' "$CFG" 2>/dev/null | cut -d= -f2 | tr -d ' ' || echo "b2")
STYLES="$ROOT/website/theme/$THEME/styles.css"
HEADER="$ROOT/website/theme/$THEME/header.html"
SCRIPTS="$ROOT/website/theme/$THEME/scripts.js"

if [ -f "$STYLES" ]; then
  # font-display: swap
  if grep -q '@font-face' "$STYLES" 2>/dev/null; then
    if ! grep -q 'font-display' "$STYLES" 2>/dev/null; then
      echo "WARN:styles.css:font_display_missing:@font-face found but no font-display: swap - fonts block rendering"
    else
      echo "OK:styles.css:font_display:font-display property found"
    fi
  fi
fi

if [ -f "$HEADER" ]; then
  # fetchpriority on hero image
  if grep -q '<img' "$HEADER" 2>/dev/null; then
    if ! grep -q 'fetchpriority' "$HEADER" 2>/dev/null; then
      echo "INFO:header.html:fetchpriority_missing:Consider fetchpriority=\"high\" on above-fold hero image"
    fi
  fi
  # scripts in head without defer
  if grep -qE '<script[^>]+src=' "$HEADER" 2>/dev/null; then
    if ! grep -qE '<script[^>]+(defer|async)' "$HEADER" 2>/dev/null; then
      echo "WARN:header.html:render_blocking_script:<script src=...> in <head> without defer - blocks rendering"
    fi
  fi
fi

if [ -f "$SCRIPTS" ]; then
  # Check if scripts.js is referenced before </body> in header - look for it in footer
  FOOTER="$ROOT/website/theme/$THEME/footer.html"
  if [ -f "$FOOTER" ]; then
    if grep -q 'scripts.js' "$FOOTER" 2>/dev/null; then
      echo "OK:scripts.js:placement:loaded in footer (non-blocking)"
    elif [ -f "$HEADER" ] && grep -q 'scripts.js' "$HEADER" 2>/dev/null; then
      echo "WARN:scripts.js:placement:loaded in <head> - move to footer or add defer for better LCP"
    fi
  fi
fi

echo "DONE:optimize:complete"
