#!/usr/bin/env bash
# assemble.sh — b2 project assembler with full SEO variable injection.
#
# Reads frontmatter from website/src/*.md and injects into header.html placeholders:
#   {{TITLE}}          page <title>
#   {{DESCRIPTION}}    meta description
#   {{CANONICAL}}      canonical URL and og:url
#   {{OG_TITLE}}       og:title (same as title)
#   {{OG_DESCRIPTION}} og:description (same as description)
#   {{OG_IMAGE}}       og:image full URL (from og_image frontmatter field)
#   {{OG_TYPE}}        article | website
#   {{LCP_PRELOAD}}    <link rel="preload"> for hero image (auto-detected)
#   {{ASSET_VERSION}}  content-hash of styles.css/scripts.js — cache-busting query param
#
# Requires: website/scripts/lcp-image.py (included alongside this template)
#
# Usage: bash website/scripts/assemble.sh
# Run from project root.

set -euo pipefail

root="$(pwd)"
cfg="$root/website/b2.cfg"
theme_name=$(grep '^THEME=' "$cfg" 2>/dev/null | cut -d= -f2 | tr -d '[:space:]')
theme_name="${theme_name:-b2}"
theme="$root/website/theme/$theme_name"
partials="$root/website/partials"
dist="$root/website/dist"
src="$root/website/src"

# --- Site configuration — edit these ---
BASE_URL="https://example.com"
DEFAULT_DESC="Replace with your site's default meta description."
DEFAULT_OG_IMAGE="${BASE_URL}/images/social-card.png"
# ----------------------------------------

[ -d "$theme" ]    || { echo "ERROR: theme not found: $theme" >&2; exit 1; }
[ -d "$partials" ] || { echo "ERROR: partials not found: $partials" >&2; exit 1; }
mkdir -p "$dist"

# Copy theme CSS and JS to dist
for f in "$theme"/*.css "$theme"/*.js; do
  [ -f "$f" ] && cp "$f" "$dist/"
done

# Cache-busting query param for /styles.css and /scripts.js — an 8-char hash of their
# own content, so the URL only changes (and old cached copies get orphaned) when the
# asset actually does. Pairs with the long-cache Cache-Control rules in website/src/.htaccess.
asset_version=$(cat "$theme"/*.css "$theme"/*.js 2>/dev/null | shasum | cut -c1-8)

# Extract a single-line frontmatter field, stripping surrounding quotes.
fm_get() {
  local file="$1" key="$2"
  grep -m1 "^${key}:" "$file" 2>/dev/null \
    | sed "s/^${key}: *//" \
    | sed 's/^[[:space:]]*//' \
    | sed 's/[[:space:]]*$//' \
    | sed 's/^"\(.*\)"$/\1/' \
    | sed "s/^'\(.*\)'$/\1/" \
    || true
}

find "$partials" -name "*.html" | LC_ALL=C sort | while read -r partial; do
  rel="${partial#$partials/}"
  out="$dist/$rel"
  mkdir -p "$(dirname "$out")"

  # Read frontmatter from corresponding src/*.md
  src_md="$src/${rel%.html}.md"
  title="" ; desc="" ; og_image=""
  if [ -f "$src_md" ]; then
    title=$(fm_get "$src_md" "title")
    desc=$(fm_get "$src_md" "description")
    og_image=$(fm_get "$src_md" "og_image")
  fi

  # Fallbacks
  [ -z "$title" ]    && title="$(basename "${rel%.html}" | sed 's/-/ /g' | sed 's/\b./\u&/g') — Site Name"
  [ -z "$desc" ]     && desc="$DEFAULT_DESC"

  # Canonical URL
  if [ "$rel" = "index.html" ]; then
    canonical="${BASE_URL}/"
  else
    canonical="${BASE_URL}/${rel}"
  fi

  # OG image (full URL)
  if [ -n "$og_image" ]; then
    og_image_url="${BASE_URL}${og_image}"
  else
    og_image_url="$DEFAULT_OG_IMAGE"
  fi

  # OG type
  case "$rel" in
    articles/*.html|blog/*.html|posts/*.html) og_type="article" ;;
    *) og_type="website" ;;
  esac

  # Auto-detect LCP image from partial (requires lcp-image.py)
  lcp_img=$(python3 "$root/website/scripts/lcp-image.py" "$partial" 2>/dev/null || true)
  if [ -n "$lcp_img" ]; then
    lcp_preload_tag="<link rel=\"preload\" href=\"${lcp_img}\" as=\"image\" fetchpriority=\"high\" />"
  else
    lcp_preload_tag=""
  fi

  # Use Python for safe string substitution (handles special chars in descriptions)
  python3 -c "
import sys
header_path, partial_path, footer_path, out_path, title, desc, canonical, og_image, og_type, lcp_preload, asset_version = sys.argv[1:]
replacements = {
    '{{TITLE}}':          title,
    '{{DESCRIPTION}}':    desc,
    '{{CANONICAL}}':      canonical,
    '{{OG_TITLE}}':       title,
    '{{OG_DESCRIPTION}}': desc,
    '{{OG_IMAGE}}':       og_image,
    '{{OG_TYPE}}':        og_type,
    '{{LCP_PRELOAD}}':    lcp_preload,
    '{{ASSET_VERSION}}':  asset_version,
}
with open(header_path) as f:
    header = f.read()
with open(footer_path) as f:
    footer = f.read()
for k, v in replacements.items():
    header = header.replace(k, v)
    footer = footer.replace(k, v)
with open(partial_path) as f:
    body = f.read()
with open(out_path, 'w') as f:
    f.write(header + body + footer)
" "$theme/header.html" "$partial" "$theme/footer.html" "$out" "$title" "$desc" "$canonical" "$og_image_url" "$og_type" "$lcp_preload_tag" "$asset_version"

  echo "  assembled: $rel"
done

echo "Assembly complete."
