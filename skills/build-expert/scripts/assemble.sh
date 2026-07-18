#!/usr/bin/env bash
# assemble.sh — build dist/ from partials + theme (fallback when make is unavailable)
# Run from the project root.

root="$(pwd)"
theme_name="b2"
cfg="$root/website/b2.cfg"
[ -f "$cfg" ] && theme_name=$(grep '^THEME=' "$cfg" | cut -d= -f2 | tr -d '[:space:]')
theme="$root/website/theme/$theme_name"
partials="$root/website/partials"
dist="$root/website/dist"

if [ ! -d "$theme" ]; then
  echo "ERROR: Theme directory not found: $theme" >&2
  exit 1
fi

if [ ! -d "$partials" ]; then
  echo "ERROR: Partials directory not found: $partials" >&2
  exit 1
fi

mkdir -p "$dist"

# Copy theme CSS and JS, incl. any vendored libraries (not mockup.html — that's a dev artifact)
for f in "$theme"/*.css "$theme"/*.js; do
  [ -f "$f" ] && cp "$f" "$dist/"
done

# Copy theme assets (self-hosted fonts, 3D models, video, etc.) so any-library designs work live
if [ -d "$theme/assets" ]; then
  mkdir -p "$dist/assets"
  cp -R "$theme/assets/." "$dist/assets/"
fi

# Assemble each partial into dist/
count=0
find "$partials" -name "*.html" | sort | while read partial; do
  rel="${partial#$partials/}"
  out="$dist/$rel"
  mkdir -p "$(dirname "$out")"
  cat "$theme/header.html" "$partial" "$theme/footer.html" > "$out"
  count=$((count + 1))
  echo "  assembled: $rel"
done

echo "Assembly complete."
