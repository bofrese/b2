#!/usr/bin/env bash
# generate-sitemap.sh — Generate sitemap.xml and robots.txt for a b2 site
# Usage: bash generate-sitemap.sh <base_url>
# Example: bash generate-sitemap.sh https://example.com
# Reads: website/dist/*.html (recursively)
# Writes: website/dist/sitemap.xml, website/dist/robots.txt (if missing)

set -euo pipefail

ROOT="$(pwd)"
DIST="$ROOT/website/dist"
BASE_URL="${1:-}"

if [ -z "$BASE_URL" ]; then
  echo "ERROR: base_url required. Usage: bash generate-sitemap.sh https://example.com"
  exit 1
fi

# Strip trailing slash
BASE_URL="${BASE_URL%/}"

if [ ! -d "$DIST" ]; then
  echo "ERROR: website/dist/ not found — run /b2:build first"
  exit 1
fi

TODAY=$(date +%Y-%m-%d)

# ────────────────────────────────────────────────────────────
# sitemap.xml
# ────────────────────────────────────────────────────────────
SITEMAP="$DIST/sitemap.xml"

cat > "$SITEMAP" << 'XMLHEADER'
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
XMLHEADER

# Find all HTML files, sorted. index.html at root = homepage (highest priority)
find "$DIST" -name "*.html" | sort | while read -r PAGE; do
  REL="${PAGE#$DIST/}"

  # Skip pages marked noindex (e.g. internal mockup/demo pages)
  if grep -q 'name="robots"[^>]*noindex' "$PAGE" 2>/dev/null; then
    continue
  fi

  # Determine URL path — b2 serves flat .html files, not pretty directory URLs
  if [ "$REL" = "index.html" ]; then
    URL_PATH="/"
    PRIORITY="1.0"
    CHANGEFREQ="weekly"
  elif [[ "$REL" == */index.html ]]; then
    DIR="${REL%/index.html}"
    URL_PATH="/$DIR/"
    PRIORITY="0.8"
    CHANGEFREQ="weekly"
  else
    URL_PATH="/$REL"
    PRIORITY="0.6"
    CHANGEFREQ="monthly"
  fi

  # Get last modified date from file mtime
  if command -v stat >/dev/null 2>&1; then
    LASTMOD=$(stat -f "%Sm" -t "%Y-%m-%d" "$PAGE" 2>/dev/null || echo "$TODAY")
  else
    LASTMOD="$TODAY"
  fi

  cat >> "$SITEMAP" << ENTRY
  <url>
    <loc>${BASE_URL}${URL_PATH}</loc>
    <lastmod>${LASTMOD}</lastmod>
    <changefreq>${CHANGEFREQ}</changefreq>
    <priority>${PRIORITY}</priority>
  </url>
ENTRY
done

echo "</urlset>" >> "$SITEMAP"

echo "WRITTEN:sitemap:$SITEMAP"

# ────────────────────────────────────────────────────────────
# robots.txt — only create if missing
# ────────────────────────────────────────────────────────────
ROBOTS="$DIST/robots.txt"
if [ ! -f "$ROBOTS" ]; then
  cat > "$ROBOTS" << ROBOTS
User-agent: *
Allow: /
Disallow: /404.html

Sitemap: ${BASE_URL}/sitemap.xml
ROBOTS
  echo "WRITTEN:robots:$ROBOTS"
else
  # Check if sitemap reference is present; if not, note it
  if ! grep -q "Sitemap:" "$ROBOTS" 2>/dev/null; then
    echo "WARN:robots:sitemap_not_referenced:Add 'Sitemap: ${BASE_URL}/sitemap.xml' to robots.txt"
  else
    echo "OK:robots:exists_unchanged:$ROBOTS"
  fi
fi

echo "DONE:generate:complete"
