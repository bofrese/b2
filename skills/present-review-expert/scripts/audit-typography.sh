#!/bin/bash
# Report font-family and font-size usage in a built presentation's index.html,
# so near-duplicate one-off sizes doing the same job become visible at a glance.
#
# Usage: audit-typography.sh <path-to-dist-index.html>
#
# Read the output looking for the same semantic role (e.g. "paragraph under a
# headline") expressed as several slightly different clamp()/rem values — that's
# the signal a reusable token is missing, not that the content genuinely needs
# that many distinct sizes. See references/typography-audit.md for what to do
# with the findings.

set -euo pipefail

FILE="${1:?Usage: audit-typography.sh <path-to-dist-index.html>}"

if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE" >&2
  exit 1
fi

echo "=== Font families in use ==="
grep -o "font-family:'[^']*'" "$FILE" | sort | uniq -c | sort -rn
echo ""
echo "(also check for unquoted monospace stacks, not counted above:)"
grep -o 'font-family:ui-monospace[^;"]*' "$FILE" | sort | uniq -c | sort -rn
echo ""

echo "=== Distinct inline font-size values ==="
echo "(each line used only once or twice is a candidate for a shared token)"
grep -o 'font-size:[^;"]*' "$FILE" | sort | uniq -c | sort -rn
echo ""

TOTAL=$(grep -o 'font-size:[^;"]*' "$FILE" | sort -u | wc -l | tr -d ' ')
echo "=== Summary ==="
echo "$TOTAL distinct inline font-size declarations found."
echo "If this number is large relative to the deck's documented type-scale roles"
echo "(check the theme's design.md Typography System table), most are probably"
echo "unintentional near-duplicates of a small number of real roles — see"
echo "references/typography-audit.md for how to consolidate them into tokens."
