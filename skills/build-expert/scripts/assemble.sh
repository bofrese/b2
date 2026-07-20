#!/usr/bin/env bash
# assemble.sh — build dist/ from partials + theme (fallback when make is unavailable)
# Injects per-page SEO values from src/*.md frontmatter into theme/header.html
# placeholders ({{TITLE}}, {{DESCRIPTION}}, {{CANONICAL}}, {{OG_TITLE}},
# {{OG_DESCRIPTION}}, {{OG_IMAGE}}, {{ROBOTS}}, {{LCP_PRELOAD}}). If the header
# has none of these placeholders (older/custom theme), this degrades to a
# plain concatenation — safe either way.
# Run from the project root.

root="$(pwd)"
theme_name="b2"
cfg="$root/website/b2.cfg"
site_url=""
[ -f "$cfg" ] && theme_name=$(grep '^THEME=' "$cfg" | cut -d= -f2 | tr -d '[:space:]')
[ -f "$cfg" ] && site_url=$(grep '^SITE_URL=' "$cfg" | cut -d= -f2 | tr -d '[:space:]')
theme="$root/website/theme/$theme_name"
partials="$root/website/partials"
dist="$root/website/dist"
src="$root/website/src"
default_og_image="${site_url}/assets/og-image.jpg"

if [ ! -d "$theme" ]; then
  echo "ERROR: Theme directory not found: $theme" >&2
  exit 1
fi

if [ ! -d "$partials" ]; then
  echo "ERROR: Partials directory not found: $partials" >&2
  exit 1
fi

mkdir -p "$dist"

# Copy theme CSS and JS, minified (pure-Python, no Node/npm dependency — see
# seo-expert/scripts/minify-css.py and minify-js.py for what's safe without a
# real parser). Includes any vendored libraries (not mockup.html — a dev artifact).
# CLAUDE_PLUGIN_ROOT is set by Claude Code when it invokes this script — falls
# back to a plain copy if it's somehow unset (e.g. run outside Claude Code).
minify_css="${CLAUDE_PLUGIN_ROOT:-}/skills/seo-expert/scripts/minify-css.py"
minify_js="${CLAUDE_PLUGIN_ROOT:-}/skills/seo-expert/scripts/minify-js.py"
for f in "$theme"/*.css; do
  [ -f "$f" ] || continue
  if [ -f "$minify_css" ]; then
    python3 "$minify_css" "$f" "$dist/$(basename "$f")"
  else
    cp "$f" "$dist/"
  fi
done
for f in "$theme"/*.js; do
  [ -f "$f" ] || continue
  if [ -f "$minify_js" ]; then
    python3 "$minify_js" "$f" "$dist/$(basename "$f")"
  else
    cp "$f" "$dist/"
  fi
done

# Copy theme assets (self-hosted fonts, 3D models, video, etc.) so any-library designs work live
if [ -d "$theme/assets" ]; then
  mkdir -p "$dist/assets"
  cp -R "$theme/assets/." "$dist/assets/"
fi

# Extract a single-line frontmatter field, stripping surrounding quotes.
fm_get() {
  local file="$1" key="$2"
  grep -m1 "^${key}:" "$file" 2>/dev/null \
    | sed "s/^${key}: *//" \
    | sed 's/^[[:space:]]*//' \
    | sed 's/[[:space:]]*$//' \
    | sed 's/^"\(.*\)"$/\1/' \
    | sed "s/^'\(.*\)'\$/\1/" \
    || true
}

# Assemble each partial into dist/
find "$partials" -name "*.html" | LC_ALL=C sort | while read -r partial; do
  rel="${partial#$partials/}"
  out="$dist/$rel"
  mkdir -p "$(dirname "$out")"

  src_md="$src/${rel%.html}.md"
  title="" ; desc="" ; og_image=""
  if [ -f "$src_md" ]; then
    title=$(fm_get "$src_md" "title")
    desc=$(fm_get "$src_md" "description")
    og_image=$(fm_get "$src_md" "og_image")
  fi

  # Fallback if frontmatter is missing title/description — derive from filename
  # rather than emit an empty <title>/<meta description>.
  [ -z "$title" ] && title="$(basename "${rel%.html}" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')"
  [ -z "$desc" ]  && desc="$title"

  if [ "$rel" = "index.html" ]; then
    canonical="${site_url}/"
  else
    canonical="${site_url}/${rel}"
  fi

  if [ -n "$og_image" ]; then
    og_image_url="${site_url}${og_image}"
  else
    og_image_url="$default_og_image"
  fi

  # Internal dev/demo pages carry noindex: true in frontmatter — everything else is indexable.
  robots_tag=""
  if [ -f "$src_md" ] && [ -n "$(fm_get "$src_md" "noindex")" ]; then
    robots_tag='<meta name="robots" content="noindex, follow" />'
  fi

  lcp_img=$(python3 "$root/b2/skills/build-expert/scripts/lcp-image.py" "$partial" 2>/dev/null || true)
  if [ -n "$lcp_img" ]; then
    lcp_preload_tag="<link rel=\"preload\" href=\"${lcp_img}\" as=\"image\" fetchpriority=\"high\" />"
  else
    lcp_preload_tag=""
  fi

  python3 -c "
import sys
header_path, out_path, partial_path, footer_path, title, desc, canonical, og_image, robots, lcp_preload = sys.argv[1:]
with open(header_path) as f:
    content = f.read()
replacements = {
    '{{TITLE}}': title,
    '{{DESCRIPTION}}': desc,
    '{{CANONICAL}}': canonical,
    '{{OG_TITLE}}': title,
    '{{OG_DESCRIPTION}}': desc,
    '{{OG_IMAGE}}': og_image,
    '{{ROBOTS}}': robots,
    '{{LCP_PRELOAD}}': lcp_preload,
}
for k, v in replacements.items():
    content = content.replace(k, v)
with open(partial_path) as f:
    body = f.read()
with open(footer_path) as f:
    footer = f.read()
with open(out_path, 'w') as f:
    f.write(content + body + footer)
" "$theme/header.html" "$out" "$partial" "$theme/footer.html" "$title" "$desc" "$canonical" "$og_image_url" "$robots_tag" "$lcp_preload_tag"

  echo "  assembled: $rel"
done

echo "Assembly complete."
