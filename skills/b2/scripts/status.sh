#!/bin/sh
# Read-only b2 project state detection. Prints KEY=value lines for /b2:b2 to parse.
# Consolidates what used to be ~7 separate file reads into one call.

theme="b2"
if [ -f website/b2.cfg ]; then
  t=$(grep -m1 '^THEME=' website/b2.cfg | cut -d= -f2)
  [ -n "$t" ] && theme="$t"
fi

has() { [ -f "$1" ] && echo yes || echo no; }
grep_line() { [ -f "$2" ] && grep -q "$1" "$2" 2>/dev/null && echo yes || echo no; }

echo "VISION=$(has docs/product/vision.md)"

if [ -f docs/product/website-design-brief.md ] || [ -f docs/product/design-brief.md ]; then
  echo "BRAND=yes"
else
  echo "BRAND=no"
fi

echo "STRUCTURE=$(has website/docs/content-types.md)"
echo "WRITE=$(grep_line '^- \[x\] Write' website/docs/status.md)"
echo "DESIGN=$(has "website/theme/$theme/components.md")"
echo "SYNC=$(grep_line '^- \[x\] Sync' website/docs/status.md)"
echo "SETUP=$(grep_line '^BUILD_TOOL=' website/b2.cfg)"
echo "THEME=$theme"

if [ -f website/docs/status.md ]; then
  inprog=$(grep -i 'IN PROGRESS' website/docs/status.md | head -1)
  echo "IN_PROGRESS=${inprog:-none}"
else
  echo "IN_PROGRESS=none"
fi
