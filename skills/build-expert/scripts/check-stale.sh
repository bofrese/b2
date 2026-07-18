#!/usr/bin/env bash
# check-stale.sh — detect stale .md files that need sync, and stale theme files
# Outputs:
#   "item:/abs/path/to/file.md"  for each stale content item
#   "index:{type}"               for each stale index file
#   "theme:/abs/path/to/file"    for each theme CSS/JS/HTML (excl. mockup.html) newer than dist/ copy
# Run from any directory; uses absolute paths.

root="$(pwd)"

# Individual content files
find "$root/website/src" -name "*.md" 2>/dev/null | while read md; do
  rel="${md#$root/website/src/}"
  html="$root/website/partials/${rel%.md}.html"
  if [ ! -f "$html" ] || [ "$md" -nt "$html" ]; then
    echo "item:$md"
  fi
done

# Index files — check each content type with Index: yes
content_types="$root/website/docs/content-types.md"
if [ -f "$content_types" ]; then
  # Extract type names (lines starting with "## " that are not "## page")
  # then check if the next "Index: yes" line follows before the next "## "
  current_type=""
  while IFS= read -r line; do
    case "$line" in
      "## "*)
        current_type="${line#\#\# }"
        ;;
      "Index: yes"*)
        if [ -n "$current_type" ]; then
          index="$root/website/partials/$current_type/index.html"
          if [ ! -f "$index" ]; then
            echo "index:$current_type"
          elif find "$root/website/src/$current_type" -name "*.md" -newer "$index" 2>/dev/null | grep -q .; then
            echo "index:$current_type"
          fi
        fi
        ;;
    esac
  done < "$content_types"
fi

# Theme files — check if any CSS/JS/HTML (excluding mockup.html) are newer than their dist/ copies
theme_name="b2"
cfg="$root/website/b2.cfg"
[ -f "$cfg" ] && theme_name=$(grep '^THEME=' "$cfg" | cut -d= -f2 | tr -d '[:space:]')
theme_dir="$root/website/theme/$theme_name"
dist_dir="$root/website/dist"
if [ -d "$theme_dir" ] && [ -d "$dist_dir" ]; then
  for f in "$theme_dir"/*.css "$theme_dir"/*.js "$theme_dir"/*.html; do
    [ -f "$f" ] || continue
    [ "$(basename "$f")" = "mockup.html" ] && continue
    base=$(basename "$f")
    if [ ! -f "$dist_dir/$base" ] || [ "$f" -nt "$dist_dir/$base" ]; then
      echo "theme:$f"
    fi
  done
fi
