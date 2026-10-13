# b2 SEO Guide - Where Things Live and How to Fix Them

This reference maps SEO concerns to specific b2 file locations. Load it during audits to know where to read and where to write fixes.

---

## b2 Build Pipeline (SEO context)

```
website/src/*.md           ← source content (Markdown + frontmatter)
         ↓ /b2:sync
website/partials/*.html    ← semantic HTML fragments (no head/header/footer)
         ↓ assemble.sh / make
website/dist/*.html        ← final pages (full HTML, what Google indexes)
```

Additionally:
```
website/theme/{THEME}/
  header.html              ← site-wide <head>, meta tags, schema, nav
  footer.html              ← site-wide footer, closing scripts
  styles.css               ← all CSS (copied to dist/)
  scripts.js               ← all JS (copied to dist/)
  components.md            ← semantic class vocabulary
  mockup.html              ← visual reference
  design.md                ← design principles
website/b2.cfg             ← THEME=, BUILD_TOOL=, BASE_PATH=
```

The THEME name comes from `website/b2.cfg` THEME= line. Default: `b2`.

---

## SEO Fix Location Map

| SEO Issue | Where to Look | Where to Fix |
|-----------|--------------|--------------|
| Missing/bad `<title>` | `dist/` page | `theme/{THEME}/header.html` (if global template) OR `src/{page}.md` frontmatter `title:` |
| Missing meta description | `dist/` page | `src/{page}.md` frontmatter `description:` - sync template must inject it |
| Missing canonical | `dist/` page | `theme/{THEME}/header.html` (add template) |
| Missing Open Graph | `dist/` page | `theme/{THEME}/header.html` |
| Missing JSON-LD schema | `dist/` page | `theme/{THEME}/header.html` (site-level) or `partials/{page}.html` (page-level) |
| Missing/wrong H1 | `dist/` page | `src/{page}.md` content - must resync via `/b2:sync` |
| Images without alt | `partials/{page}.html` | Edit `partials/{page}.html` directly; or fix in `src/{page}.md` and resync |
| Missing lang on `<html>` | `dist/` page | `theme/{THEME}/header.html` - add `lang="en"` to `<html>` tag |
| Missing viewport | `dist/` page | `theme/{THEME}/header.html` |
| Missing sitemap.xml | `dist/` | Generate with `scripts/generate-sitemap.sh` |
| Missing robots.txt | `dist/` | Generate with `scripts/generate-sitemap.sh` |
| Thin content | `src/{page}.md` | Rewrite source, resync, rebuild |
| Bad URL structure | Config / hosting | BASE_PATH in `b2.cfg`; URL slug = src filename minus `.md` |
| Missing semantic landmarks | `partials/{page}.html` | Edit partial; or fix in header/footer for nav/header/footer |
| Duplicate titles | Multiple `src/*.md` | Update frontmatter `title:` in each affected source file |

---

## Reading the Config

Always start an SEO session with:

```bash
# Get theme name
THEME=$(grep '^THEME=' website/b2.cfg 2>/dev/null | cut -d= -f2 | tr -d ' ')
THEME="${THEME:-b2}"
BASE_PATH=$(grep '^BASE_PATH=' website/b2.cfg 2>/dev/null | cut -d= -f2 | tr -d ' ')
BASE_PATH="${BASE_PATH:-/}"
echo "Theme: $THEME | Base path: $BASE_PATH"
```

---

## Inspecting the Header Template

The header template is the highest-leverage SEO file in a b2 site. It controls what appears in `<head>` for every page. Read it with:

```
Read: website/theme/{THEME}/header.html
```

Check for:
- `<title>` - is it static or uses a variable like `{{title}}` or `<!-- title -->`?
- `<meta name="description" ...>` - present and variable?
- `<link rel="canonical" ...>` - present?
- `<meta property="og:*" ...>` - Open Graph block?
- `<html lang="...">` - lang attribute?
- `<meta name="viewport" ...>` - present?
- `<script type="application/ld+json">` - schema block?

If the header uses a static title and no frontmatter injection, the fix is to update `header.html` to use the b2 assembly variable syntax OR to write page-specific titles into partials.

**b2 assembly variable syntax** - check `assemble.sh` or the Makefile to understand how `header.html` is assembled with each page. b2 may inject frontmatter values using sed substitution, template variables, or include logic. Look at existing dist/ pages to understand what's actually rendered before proposing template changes.

---

## Reading Source Content for SEO

Source files are Markdown with YAML frontmatter. Example:

```markdown
---
title: "SEO Audit for Small Businesses"
description: "Step-by-step SEO audit guide for small business owners."
date: 2026-04-14
---

# SEO Audit for Small Businesses

Content here...
```

The `title` and `description` frontmatter fields are what drive `<title>` and `<meta name="description">` in the assembled output - IF the header template is wired up to inject them.

To check how many src files have proper frontmatter:
```bash
for f in website/src/*.md website/src/**/*.md; do
  [ -f "$f" ] || continue
  HAS_TITLE=$(grep -c '^title:' "$f" 2>/dev/null || true)
  HAS_DESC=$(grep -c '^description:' "$f" 2>/dev/null || true)
  REL="${f#website/src/}"
  echo "src:$REL:title=$HAS_TITLE:desc=$HAS_DESC"
done
```

---

## Fixing the Header Template for SEO

When `website/theme/{THEME}/header.html` is missing SEO tags, add them. The assembly mechanism determines how page-specific values get inserted.

**Pattern to check first** - look at an existing `dist/` page. If title is already page-specific, the template already injects it. If title is the same on every page, the template is static and needs updating.

**Common b2 assembly patterns:**

1. **sed substitution** - `assemble.sh` replaces `{{TITLE}}` tokens in the header with values from frontmatter.
2. **Makefile variables** - title and description passed as Makefile variables.
3. **Static** - no injection; each page has the same title from the template.

Read `assemble.sh` at `${CLAUDE_PLUGIN_ROOT}/skills/build-expert/scripts/assemble.sh` or the project's `website/Makefile` to understand which pattern is in use before editing the template.

---

## Schema Markup Patterns for b2 Sites

### Site-level schema (header.html)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "SITE_NAME",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://linkedin.com/company/...",
    "https://twitter.com/..."
  ]
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "SITE_NAME",
  "url": "https://example.com"
}
</script>
```

### Page-level schema (in partials)

For articles/blog posts - add to the partial:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title Here",
  "datePublished": "2026-04-14",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  }
}
</script>
```

For FAQ sections:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text here?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text here."
      }
    }
  ]
}
</script>
```

---

## Sitemap and Robots - b2 Specifics

b2 does not auto-generate `sitemap.xml` or `robots.txt`. These must be:
1. Generated by `scripts/generate-sitemap.sh` (part of this skill)
2. OR created manually and placed in `website/dist/` (they won't be overwritten by make/assemble)
3. OR placed in `website/src/` as static files that get copied during assembly (if the Makefile/assemble.sh supports this)

**Check Makefile/assemble.sh** to see if static files in `website/src/` are copied to `dist/`. If so, place `sitemap.xml` and `robots.txt` there for persistence across builds.

**BASE_PATH consideration**: if `BASE_PATH` in `b2.cfg` is not `/` (e.g., `/mysite`), the sitemap URLs must include the base path. The `generate-sitemap.sh` script uses the provided base URL directly - ensure you pass the full URL including path prefix.

---

## Build System Variable Injection

**Critical check before any per-page meta work.** If header.html has no `{{TITLE}}` placeholder, per-page titles and descriptions CANNOT be injected - every page will share the same hardcoded values from the template. This must be fixed first.

**Detection:**
```bash
grep -c '{{' website/theme/${THEME}/header.html
# 0 → static header, injection not set up
# >0 → already templated
```

**If header is static:** The site needs a project-level `assemble.sh` that reads frontmatter and injects values. The `website/scripts/` directory is the right location. A complete reference template is in `references/assemble-template.sh` in this skill.

**Header.html placeholders to add:**
```html
<title>{{TITLE}}</title>
<meta name="description" content="{{DESCRIPTION}}" />
<link rel="canonical" href="{{CANONICAL}}" />
<meta property="og:type" content="{{OG_TYPE}}" />
<meta property="og:title" content="{{OG_TITLE}}" />
<meta property="og:description" content="{{OG_DESCRIPTION}}" />
<meta property="og:url" content="{{CANONICAL}}" />
<meta property="og:image" content="{{OG_IMAGE}}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:site_name" content="SITE_NAME" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{{OG_TITLE}}" />
<meta name="twitter:description" content="{{OG_DESCRIPTION}}" />
<meta name="twitter:image" content="{{OG_IMAGE}}" />
{{LCP_PRELOAD}}
```

**Frontmatter fields used by the assembler:**
| Field | Required | Notes |
|-------|----------|-------|
| `title` | Yes | Page-specific `<title>` tag |
| `description` | Yes | Meta description |
| `og_image` | Yes | Path e.g. `/images/about-og-image.webp` - relative, assembled to full URL |

Pages without these fields fall back to site-wide defaults defined in assemble.sh.

---

## og:image Auto-Generation

**og:image is NOT an external problem.** If the page already has a hero illustration or photo, a 1200×630 crop can be generated automatically.

**Approach:** center-crop the first usable `<img>` in each partial to 1200×630px, save as WebP.

**Script:**
```bash
# Audit - see what would be created
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/create-og-images.py" audit

# Create all og:images
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/create-og-images.py" fix
```

Output: `{slug}-og-image.webp` in `website/dist/images/`.

**After running:** add `og_image: /images/{slug}-og-image.webp` to each src/*.md frontmatter. The assembler then injects it as a full URL in the `og:image` meta tag.

Only classify og:image as EXTERNAL if the page has NO existing image (e.g., a text-only landing page with no illustrations). In that case: `/b2:illustrate` or `/b2:image`.

---

## Font Self-Hosting

**Any external font CDN causes FCP delays**, not just Google Fonts. Every page load requires DNS lookups + TLS handshakes to each external origin before text can render - a design with two foundries (e.g. Google Fonts for body text, Fontshare/Adobe Fonts/Bunny Fonts for display headings) pays this cost twice. Check for **all** of them, not just the first one found - a second CDN is easy to miss because a similar-looking fix (self-hosting the first one) already ran and the page "looks handled."

**Detection and fix are the same step** - the script fetches every external `<link rel="stylesheet">` in header.html and keeps whichever ones actually serve `@font-face` CSS (provider-agnostic, no per-CDN special-casing):
```bash
# Audit - see what would be downloaded, from every detected font CDN
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/selfhost-fonts.py" audit

# Download Latin-subset (or, for providers that don't split by subset, all) woff2
# files, patch styles.css, and patch header.html directly
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/selfhost-fonts.py" fix
```

The script:
1. Finds every external stylesheet link in header.html, fetches each, keeps the ones containing `@font-face`
2. Downloads the `/* latin */` subset woff2 files where the provider splits by subset (Google Fonts convention); downloads everything where it doesn't (many other foundries ship one universal file per weight - Fontshare, for example)
3. Generates `@font-face` rules with `font-display: swap` → prepends to `styles.css` (both theme and dist copies)
4. **Patches header.html directly** - removes the CDN `<link>`/`<preconnect>` tags, adds `<link rel="preload">` for the base (400, non-italic) weight of each family. No manual follow-up edit needed.

**Variable fonts are not a bug:** modern Google Fonts responses often serve ONE woff2 file covering an entire weight range, with several `@font-face` blocks (one per discrete weight, e.g. 400/500/600/700) all pointing at that same file. This is standard, correct technique - browsers instantiate the right weight from the file's variable axis. Don't "fix" it into separate per-weight downloads; the script already handles this correctly via URL deduplication.

**After running:** rebuild (`make` or `assemble.sh`) - no manual header.html edit needed, the script already applied it.

**Expected FCP improvement:** 1–3s → typically halves FCP (eliminated cross-origin DNS + TLS round trips) per CDN removed. Observed: 3.5s → 1.1s in one real-world case with two CDNs self-hosted.

---

## LCP Preload Pattern

**`fetchpriority="high"` alone is not enough for LCP.** It tells the browser to prioritise the image once discovered - but discovery still happens during body parsing, which is after CSS download and initial render. A `<link rel="preload">` in `<head>` starts the fetch during HTML parsing, before any CSS or JS loads.

**Pattern:** The `{{LCP_PRELOAD}}` placeholder in header.html gets replaced by assemble.sh with a per-page preload tag auto-detected from the partial.

**Auto-detection in assemble.sh:** find the first `<img>` line containing `fetchpriority=high` and extract its src. This works because `fix-img-tags.py` already marks the first image in each partial with `fetchpriority="high"`.

**assemble.sh snippet:**
```bash
lcp_img=$(python3 scripts/lcp-image.py "$partial" 2>/dev/null || true)
if [ -n "$lcp_img" ]; then
  lcp_preload_tag="<link rel=\"preload\" href=\"${lcp_img}\" as=\"image\" fetchpriority=\"high\" />"
else
  lcp_preload_tag=""
fi
```

With companion script `website/scripts/lcp-image.py`:
```python
import re, sys
with open(sys.argv[1]) as f:
    content = f.read()
for line in content.splitlines():
    if 'fetchpriority' in line and 'high' in line and '<img' in line:
        m = re.search(r'src=["\']([^"\']+)["\']', line)
        if m:
            print(m.group(1))
            break
```

**Expected LCP improvement:** eliminates the discovery-delay gap between FCP and LCP. Observed: reduced LCP from 4.4s (post-font-fix) toward FCP baseline.

---

## Page Speed - b2 Context

b2 sites are static HTML - inherently fast. Common CWV issues in b2 sites:

**FCP (first text/paint):**
- Google Fonts CDN is the most common FCP killer - self-host instead (see Font Self-Hosting above).
- Any render-blocking third-party script in `<head>` without `defer` adds latency.
- Check **every** CDN font, not just Google Fonts - a font-heavy design commonly loads two or three foundries at once (e.g., Google Fonts for body text, Fontshare/Adobe Fonts for display headings). `selfhost-fonts.py` only handles Google Fonts; a second CDN with the same render-blocking cost is easy to miss because it "already looks handled."

**LCP:**
- The LCP element is not always an image - it can be a text node (a hero heading, a styled span). Don't assume; when a PageSpeed check shows a persistently poor LCP with no obvious image cause, query the `lcp-breakdown-insight` audit (not surfaced by the summary script - call the API directly) for the actual element and its `elementRenderDelay` vs `timeToFirstByte` split. A near-zero TTFB with a large render delay means the resource loaded fine and something on the main thread is delaying paint - not a resource-loading problem, a scheduling one.
- If LCP is an image: add `<link rel="preload">` in `<head>` (auto-injected via `{{LCP_PRELOAD}}` in assemble.sh), `fetchpriority="high"` + `loading="eager"` on the tag, WebP, sized to actual display dimensions.

**General principle - sequence, don't cut:** a slow paint is usually a scheduling problem, not a "too much visual richness" problem. Never propose removing an animation, background effect, or decorative element to fix a speed score - reorder it instead. Anything not needed for first paint (ambient canvas/particle backgrounds, parallax fields, decorative mascots, glitch/glow effects) should initialize after first paint, not before or during it: gate with `requestIdleCallback(fn, { timeout: N })` (with a `setTimeout` fallback for browsers without it) or a `window.load` listener, respecting `prefers-reduced-motion` throughout. This site's own `scripts.js` already does this correctly for its starfield canvas and parallax space objects - treat that as the reference pattern, not a one-off. The only case for actually cutting an effect is if the user decides the tradeoff isn't worth it - that's their call to make, not a default fix.

**CLS (layout shift)**:
- All images need `width` and `height` attributes - `fix-img-tags.py` handles this.
- Fonts: `font-display: swap` prevents invisible text during font load.

**Render-blocking resources**:
- CSS `<link>` in `<head>` is correct - do not add `async`/`defer` to stylesheets.
- Every `<script>` tag - first-party (`scripts.js`) and third-party (e.g., Lucide from unpkg.com) alike - needs `defer` unless it has a specific reason to run synchronously. Being placed at the end of `<body>` is not equivalent to `defer`: an un-deferred script there still blocks parsing/paint while it downloads and executes.

**PageSpeed workflow:** use `/b2:seo pagespeed` (PageSpeed Check Mode) - it calls the API directly via `scripts/pagespeed-check.py`, no manual site visits needed. Test mobile and desktop both; a healthy desktop score with a poor mobile score usually means render-blocking CDN resources (fonts, scripts), since mobile is CPU/network-throttled in Lighthouse and desktop isn't. Common pattern: font self-hosting → FCP drops, `defer` on remaining scripts → LCP render-delay drops, LCP preload → LCP fetch-delay drops.

---

## Content Inventory (quick bash)

Get a view of all src content and their SEO readiness:
```bash
echo "FILE | TITLE | DESCRIPTION | WORD_COUNT"
for f in $(find website/src -name "*.md" | sort); do
  REL="${f#website/src/}"
  TITLE=$(grep '^title:' "$f" 2>/dev/null | head -1 | sed 's/title: *//' | tr -d '"' || echo "MISSING")
  DESC=$(grep '^description:' "$f" 2>/dev/null | head -1 | sed 's/description: *//' | tr -d '"' || echo "MISSING")
  WC=$(cat "$f" | wc -w | tr -d ' ')
  echo "$REL | $TITLE | $DESC | ${WC}w"
done
```
