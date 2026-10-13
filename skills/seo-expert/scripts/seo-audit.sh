#!/usr/bin/env bash
# seo-audit.sh - b2 SEO audit across website/dist/
# Compatible with: macOS BSD grep (no -P), bash 3.2+
#
# Usage: bash seo-audit.sh [optional: specific page e.g. about.html]
# Output: structured lines prefixed by category for parsing

set -uo pipefail

ROOT="$(pwd)"
DIST="$ROOT/website/dist"
PAGE_ARG="${1:-}"

if [ ! -d "$DIST" ]; then
  echo "ERROR:dist_missing:website/dist/ not found - run /b2:build first"
  exit 1
fi

# Collect pages to audit
if [ -n "$PAGE_ARG" ]; then
  if [ -f "$DIST/$PAGE_ARG" ]; then
    PAGES="$DIST/$PAGE_ARG"
  else
    echo "ERROR:page_missing:$PAGE_ARG not found in website/dist/"
    exit 1
  fi
else
  PAGES=$(find "$DIST" -name "*.html" | sort)
fi

if [ -z "$PAGES" ]; then
  echo "ERROR:no_html:No .html files found in website/dist/"
  exit 1
fi

# ── Helper: extract attribute value from HTML ──────────────
# extract_attr <content> <pattern_to_isolate_value>
# We use sed with basic extended regex (works on macOS)

# ────────────────────────────────────────────────────────────
# Per-page checks
# ────────────────────────────────────────────────────────────
for PAGE in $PAGES; do
  REL="${PAGE#$DIST/}"
  CONTENT=$(cat "$PAGE")

  # ── Title tag ──────────────────────────────────────────────
  TITLE=$(echo "$CONTENT" | grep -oE '<title>[^<]+' | sed 's/<title>//' | head -1 || true)
  if [ -z "$TITLE" ]; then
    echo "ISSUE:$REL:title_missing:No <title> tag found"
  else
    LEN=${#TITLE}
    if [ "$LEN" -gt 60 ]; then
      echo "WARN:$REL:title_long:${LEN} chars (ideal: 50-60) - \"$TITLE\""
    elif [ "$LEN" -lt 20 ]; then
      echo "WARN:$REL:title_short:${LEN} chars (too short) - \"$TITLE\""
    else
      echo "OK:$REL:title:\"$TITLE\" (${LEN} chars)"
    fi
  fi

  # ── Meta description ───────────────────────────────────────
  # Handle both attribute orderings: name=... content=... and content=... name=...
  META_DESC=$(echo "$CONTENT" \
    | grep -oE 'name="description"[^>]*content="[^"]*"' \
    | grep -oE 'content="[^"]*"' \
    | sed 's/content="\([^"]*\)"/\1/' \
    | head -1 || true)
  if [ -z "$META_DESC" ]; then
    META_DESC=$(echo "$CONTENT" \
      | grep -oE 'content="[^"]*"[^>]*name="description"' \
      | grep -oE 'content="[^"]*"' \
      | sed 's/content="\([^"]*\)"/\1/' \
      | head -1 || true)
  fi
  if [ -z "$META_DESC" ]; then
    echo "ISSUE:$REL:meta_desc_missing:No meta description found"
  else
    LEN=${#META_DESC}
    if [ "$LEN" -gt 160 ]; then
      echo "WARN:$REL:meta_desc_long:${LEN} chars (ideal: 150-160)"
    elif [ "$LEN" -lt 50 ]; then
      echo "WARN:$REL:meta_desc_short:${LEN} chars (too short)"
    else
      echo "OK:$REL:meta_desc:${LEN} chars"
    fi
  fi

  # ── H1 tag ─────────────────────────────────────────────────
  H1_COUNT=$(echo "$CONTENT" | grep -c '<h1' || true)
  if [ "$H1_COUNT" -eq 0 ]; then
    echo "ISSUE:$REL:h1_missing:No <h1> found"
  elif [ "$H1_COUNT" -gt 1 ]; then
    echo "WARN:$REL:h1_multiple:${H1_COUNT} <h1> tags found (should be 1)"
  else
    H1_TEXT=$(echo "$CONTENT" | grep -oE '<h1[^>]*>[^<]+' | sed 's/<[^>]*>//' | head -1 || true)
    echo "OK:$REL:h1:\"$H1_TEXT\""
  fi

  # ── Canonical tag ──────────────────────────────────────────
  CANONICAL=$(echo "$CONTENT" \
    | grep -oE '<link[^>]*rel="canonical"[^>]*>' \
    | grep -oE 'href="[^"]*"' \
    | sed 's/href="\([^"]*\)"/\1/' \
    | head -1 || true)
  if [ -z "$CANONICAL" ]; then
    echo "WARN:$REL:canonical_missing:No canonical link tag"
  else
    echo "OK:$REL:canonical:$CANONICAL"
  fi

  # ── Open Graph tags ────────────────────────────────────────
  OG_TITLE=$(echo "$CONTENT" | grep -c 'property="og:title"' || true)
  OG_DESC=$(echo "$CONTENT" | grep -c 'property="og:description"' || true)
  OG_IMAGE=$(echo "$CONTENT" | grep -c 'property="og:image"' || true)
  if [ "$OG_TITLE" -eq 0 ] || [ "$OG_DESC" -eq 0 ]; then
    echo "WARN:$REL:og_incomplete:Missing og:title or og:description"
  else
    echo "OK:$REL:opengraph:title+desc present"
  fi
  if [ "$OG_IMAGE" -eq 0 ]; then
    echo "WARN:$REL:og_image_missing:No og:image tag"
  else
    OG_IMAGE_PATH=$(echo "$CONTENT" \
      | grep -oE 'property="og:image"[^>]*content="[^"]*"' \
      | grep -oE 'content="[^"]*"' \
      | sed 's/content="\([^"]*\)"/\1/' \
      | head -1 || true)
    if [ -n "$OG_IMAGE_PATH" ]; then
      OG_IMAGE_LOCAL=$(echo "$OG_IMAGE_PATH" | sed -E 's#^https?://[^/]+##')
      if [ ! -f "$DIST$OG_IMAGE_LOCAL" ]; then
        echo "ISSUE:$REL:og_image_broken:og:image points to $OG_IMAGE_PATH - file not found in dist/"
      fi
    fi
  fi

  # ── Unfilled template placeholders (assemble.sh regression) ─
  UNFILLED=$(echo "$CONTENT" | grep -oE '\{\{[A-Z_]+\}\}' | sort -u | tr '\n' ' ')
  if [ -n "$UNFILLED" ]; then
    echo "ISSUE:$REL:unfilled_placeholder:literal template vars in output: $UNFILLED"
  fi

  # ── Images without alt ─────────────────────────────────────
  # Count total <img> tags, subtract those that have alt=
  IMG_TOTAL=$(echo "$CONTENT" | grep -c '<img ' || true)
  IMG_WITH_ALT=$(echo "$CONTENT" | grep -cE '<img [^>]*alt=' || true)
  IMG_NO_ALT=$(( IMG_TOTAL - IMG_WITH_ALT ))
  if [ "$IMG_NO_ALT" -gt 0 ]; then
    echo "ISSUE:$REL:img_no_alt:${IMG_NO_ALT} image(s) missing alt attribute"
  fi

  # ── Images with empty alt ──────────────────────────────────
  IMG_EMPTY_ALT=$(echo "$CONTENT" | grep -cE 'alt=""' || true)
  if [ "$IMG_EMPTY_ALT" -gt 0 ]; then
    echo "WARN:$REL:img_empty_alt:${IMG_EMPTY_ALT} image(s) with empty alt (OK for decorative only)"
  fi

  # ── Heading hierarchy ──────────────────────────────────────
  H2_COUNT=$(echo "$CONTENT" | grep -c '<h2' || true)
  H3_COUNT=$(echo "$CONTENT" | grep -c '<h3' || true)
  if [ "$H3_COUNT" -gt 0 ] && [ "$H2_COUNT" -eq 0 ]; then
    echo "WARN:$REL:heading_hierarchy:<h3> found without <h2> - skipped heading level"
  fi

  # ── Structured data / JSON-LD ──────────────────────────────
  JSONLD=$(echo "$CONTENT" | grep -c 'application/ld+json' || true)
  if [ "$JSONLD" -eq 0 ]; then
    echo "WARN:$REL:schema_missing:No JSON-LD structured data"
  else
    echo "OK:$REL:schema:JSON-LD present"
  fi

  # ── Lang attribute ─────────────────────────────────────────
  LANG=$(echo "$CONTENT" \
    | grep -oE '<html[^>]*lang="[^"]*"' \
    | grep -oE 'lang="[^"]*"' \
    | sed 's/lang="\([^"]*\)"/\1/' \
    | head -1 || true)
  if [ -z "$LANG" ]; then
    echo "WARN:$REL:lang_missing:No lang attribute on <html>"
  else
    echo "OK:$REL:lang:$LANG"
  fi

  # ── Viewport meta ──────────────────────────────────────────
  VIEWPORT=$(echo "$CONTENT" | grep -c 'name="viewport"' || true)
  if [ "$VIEWPORT" -eq 0 ]; then
    echo "ISSUE:$REL:viewport_missing:No viewport meta tag (mobile indexing will fail)"
  fi

  # ── Favicon ─────────────────────────────────────────────────
  FAVICON=$(echo "$CONTENT" | grep -c 'rel="icon"' || true)
  if [ "$FAVICON" -eq 0 ]; then
    echo "ISSUE:$REL:favicon_missing:No <link rel=\"icon\"> found - see design-expert's generate-favicon.py"
  fi

  # ── Semantic landmarks ─────────────────────────────────────
  HAS_MAIN=$(echo "$CONTENT" | grep -c '<main' || true)
  HAS_NAV=$(echo "$CONTENT" | grep -c '<nav' || true)
  HAS_HEADER=$(echo "$CONTENT" | grep -c '<header' || true)
  HAS_FOOTER=$(echo "$CONTENT" | grep -c '<footer' || true)
  MISSING_LANDMARKS=""
  [ "$HAS_MAIN" -eq 0 ] && MISSING_LANDMARKS="${MISSING_LANDMARKS}<main> "
  [ "$HAS_NAV" -eq 0 ] && MISSING_LANDMARKS="${MISSING_LANDMARKS}<nav> "
  [ "$HAS_HEADER" -eq 0 ] && MISSING_LANDMARKS="${MISSING_LANDMARKS}<header> "
  [ "$HAS_FOOTER" -eq 0 ] && MISSING_LANDMARKS="${MISSING_LANDMARKS}<footer> "
  if [ -n "$MISSING_LANDMARKS" ]; then
    echo "WARN:$REL:landmarks_missing:Missing semantic landmarks: $MISSING_LANDMARKS"
  fi

  # ── Internal links ─────────────────────────────────────────
  LINK_COUNT=$(echo "$CONTENT" | grep -c '<a href' || true)
  echo "INFO:$REL:internal_links:${LINK_COUNT} anchor tag(s)"

  # ── Word count estimate ────────────────────────────────────
  WORD_COUNT=$(echo "$CONTENT" | sed 's/<[^>]*>//g' | wc -w | tr -d ' ')
  if [ "$WORD_COUNT" -lt 300 ]; then
    echo "WARN:$REL:thin_content:~${WORD_COUNT} words (thin page - <300)"
  else
    echo "OK:$REL:word_count:~${WORD_COUNT} words"
  fi

  # ── HTTPS refs ─────────────────────────────────────────────
  HTTP_REFS=$(echo "$CONTENT" | grep -cE 'href="http://' || true)
  if [ "$HTTP_REFS" -gt 0 ]; then
    echo "WARN:$REL:mixed_content:${HTTP_REFS} href(s) using http:// (should be https://)"
  fi

done

# ────────────────────────────────────────────────────────────
# Site-level checks
# ────────────────────────────────────────────────────────────

# ── robots.txt ────────────────────────────────────────────
if [ -f "$DIST/robots.txt" ]; then
  echo "OK:site:robots_txt:Found website/dist/robots.txt"
  if grep -qE "^Disallow:[[:space:]]*/[[:space:]]*$" "$DIST/robots.txt" 2>/dev/null; then
    echo "ISSUE:site:robots_blocking:robots.txt contains Disallow: / - may block all crawling"
  fi
else
  echo "ISSUE:site:robots_txt_missing:No robots.txt in website/dist/"
fi

# ── sitemap.xml ───────────────────────────────────────────
if [ -f "$DIST/sitemap.xml" ]; then
  SITEMAP_PAGES=$(grep -c '<url>' "$DIST/sitemap.xml" 2>/dev/null || echo "0")
  echo "OK:site:sitemap:Found sitemap.xml with ${SITEMAP_PAGES} URL(s)"
else
  echo "ISSUE:site:sitemap_missing:No sitemap.xml in website/dist/"
fi

# ── Duplicate titles (awk-based, bash 3.2 compatible) ─────
TMPFILE=$(mktemp /tmp/seo-titles.XXXXXX)
for PAGE in $PAGES; do
  REL="${PAGE#$DIST/}"
  T=$(grep -oE '<title>[^<]+' "$PAGE" 2>/dev/null | sed 's/<title>//' | head -1 || true)
  if [ -n "$T" ]; then
    echo "$T|$REL" >> "$TMPFILE"
  fi
done

awk -F'|' '
{
  count[$1]++
  files[$1] = files[$1] " " $2
}
END {
  for (t in count) {
    if (count[t] > 1) {
      print "ISSUE:site:duplicate_title:\"" t "\" used in:" files[t]
    }
  }
}
' "$TMPFILE"
rm -f "$TMPFILE"

echo "DONE:audit:complete"
