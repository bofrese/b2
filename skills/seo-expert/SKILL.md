---
name: seo-expert
description: This skill should be used when the user runs "/b2:seo", asks to "audit SEO", "fix SEO", "fix all SEO issues", "improve search ranking", "check meta tags", "add sitemap", "add robots.txt", "add schema markup", "check page titles", "check meta descriptions", "add Open Graph tags", "improve Core Web Vitals", "fix loading time", "convert images to WebP", "optimise images", "check for SEO issues", or asks any question about SEO strategy, keyword optimisation, backlinks, featured snippets, or search engine optimisation for their b2 website.
version: 0.2.0
---

# b2 SEO Expert

Full-cycle SEO: audit, fix, dialog for issues needing input, and advise on what can only be done externally. Operates directly on the b2 pipeline — reads `website/dist/` for issues, fixes at the correct layer (`src/`, `partials/`, `theme/`), rebuilds.

---

## Before Starting

1. Read `website/b2.cfg` to get `THEME=` and `BASE_PATH=`. Defaults: `THEME=b2`, `BASE_PATH=/`.
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/references/b2-seo-guide.md` — required for all audit and fix work.
3. Check for an argument:
   - No argument → **Full Fix Mode** (audit everything, fix everything)
   - Specific page (e.g., `about.html`) → run Full Fix Mode scoped to that page
   - Category keyword (`images`, `schema`, `sitemap`, `content`, `performance`) → targeted mode
   - Question or strategy request → **Coaching Mode** (load `references/seo-knowledge.md`)

---

## Full Fix Mode — Master Workflow

This is the primary mode. It audits the entire site, classifies every issue by how it can be resolved, fixes everything it can automatically, and enters a structured dialog for anything requiring human input.

### Phase 1 — Collect All Evidence

Run all detection in parallel:

**HTML audit** (Bash):
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/seo-audit.sh"
```

**Image + performance audit** (Bash):
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/optimize-images.sh" audit
```

**Img tag audit** (Bash):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/fix-img-tags.py" audit
```

**og:image audit** (Bash):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/create-og-images.py" audit
```

**Font CDN check** (Bash):
```bash
grep -c 'fonts.googleapis' website/theme/${THEME}/header.html 2>/dev/null || echo "0"
```

**Build system check** (Bash):
```bash
# 0 = static header (no variable injection), >0 = already templated
grep -c '{{' website/theme/${THEME}/header.html 2>/dev/null || echo "0"
```

**Content inventory** (Bash):
```bash
for f in $(find website/src -name "*.md" 2>/dev/null | sort); do
  REL="${f#website/src/}"
  TITLE=$(grep '^title:' "$f" 2>/dev/null | head -1 | sed 's/title: *//' | tr -d '"' || echo "MISSING")
  DESC=$(grep '^description:' "$f" 2>/dev/null | head -1 | sed 's/description: *//' | tr -d '"' || echo "MISSING")
  WC=$(wc -w < "$f" | tr -d ' ')
  echo "$REL|$TITLE|$DESC|${WC}"
done
```

**Header template** (Read tool): `website/theme/{THEME}/header.html`

### Phase 2 — Classify Every Issue

Sort all findings into four buckets:

| Bucket | Meaning | Action |
|--------|---------|--------|
| **AUTO** | Can be fixed immediately, no info needed | Fix without asking |
| **ONE_QUESTION** | Need one piece of info (e.g., base URL), then can auto-fix | Ask once, then fix |
| **DIALOG** | Need back-and-forth (e.g., alt text, descriptions) | Structured conversation |
| **EXTERNAL** | Can't be fixed in code — provide exact steps | Print instructions |

**STRUCTURAL issues** (must fix before per-page meta work can proceed):
- `header.html` has no `{{TITLE}}` placeholder (static header) → create `website/scripts/assemble.sh` using template from `references/assemble-template.sh`, then update `header.html` with all placeholders. See `references/b2-seo-guide.md` — "Build System Variable Injection".

**AUTO issues** (fix silently in Phase 3):
- Missing `lang` on `<html>` → add to `header.html`
- Missing `<meta name="viewport">` → add to `header.html`
- Missing `font-display: swap` in CSS `@font-face` → patch `styles.css`
- Any third-party `<script>` in `<head>` without `defer` → add `defer` attribute (Lucide, analytics, etc.)
- `<img>` missing `width`/`height` (dimensions detectable) → `fix-img-tags.py fix`
- `<img>` missing `loading` attribute → `fix-img-tags.py fix`
- Missing `robots.txt` (once URL known from ONE_QUESTION)
- Missing `sitemap.xml` (once URL known from ONE_QUESTION)
- Google Fonts CDN detected → self-host using `selfhost-fonts.py fix` (see `references/b2-seo-guide.md`)
- og:image missing but page images exist → auto-generate 1200×630 crops using `create-og-images.py fix`
- LCP preload missing → add `{{LCP_PRELOAD}}` to `header.html` + update `assemble.sh` to inject it (see `references/b2-seo-guide.md` — "LCP Preload Pattern")

**ONE_QUESTION issues**:
- Missing `<link rel="canonical">` → need: base URL
- Missing Open Graph `og:url` → need: base URL
- Missing `sitemap.xml` + `robots.txt` → need: base URL

**DIALOG issues**:
- Missing `Organization` / `WebSite` JSON-LD schema → need: site name, description, social links, logo
- Missing alt text on images → propose alt text from filename/context, confirm per image
- Missing `<title>` tags → propose from content, confirm
- Missing meta descriptions → propose from content, confirm
- Duplicate title tags → show both pages, ask which to change

**EXTERNAL issues** (print exact steps, cannot fix in files):
- Google Search Console not set up
- PageSpeed/CWV score unknown (must test externally — share results to fix LCP/FCP in code)
- No backlinks (strategy advice only)
- og:image missing AND no page images exist (no source to crop — must create with `/b2:illustrate`)

### Phase 3 — Present the Plan

Before touching anything, output the classification:

```
SEO Audit Complete — [site name]

AUTO (will fix now — no input needed): N issues
  ✓ Missing lang="en" on <html>
  ✓ Missing viewport meta
  ✓ 4 <img> tags missing width/height (dimensions detected)
  ✓ 6 <img> tags missing loading attribute
  ✓ scripts.js in <head> missing defer

ONE QUESTION (need 1 answer, then auto-fix): N issues
  ? What is the live URL of this site? (e.g., https://example.com)
    → Will fix: canonical tags, sitemap.xml, robots.txt, og:url

DIALOG (need your input): N issues
  💬 Organization schema — need: site name, social links
  💬 3 images missing alt text — will propose, confirm each
  💬 index.html meta description missing — will propose from content

EXTERNAL (you need to do these — exact steps below): N issues
  ⚠ Google Search Console not set up
  ⚠ PageSpeed score unknown — test at pagespeed.web.dev

HANDOFF: N issues
  → 2 thin pages — run /b2:write to rewrite them

Fix everything above? (yes / no / start with AUTO only)
```

Wait for confirmation before writing anything.

### Phase 4 — Execute AUTO Fixes

Apply all AUTO fixes using Read + Edit tools. Work file by file.

**header.html fixes** — read the file first, then apply all header fixes in a single edit pass:
- Add `lang="en"` to `<html>` tag
- Add `<meta name="viewport" content="width=device-width, initial-scale=1">` if missing
- Note: never add duplicate tags — check before adding

**styles.css fix** — read, then add `font-display: swap` to each `@font-face` block that lacks it.

**scripts.js placement** — read header.html and footer.html; either add `defer` to the script tag, or move it to footer.

**img tag fixes** (Bash):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/fix-img-tags.py" fix
```

Report each AUTO fix as it completes:
```
✓ header.html — added lang="en", viewport meta
✓ styles.css — added font-display: swap to 2 @font-face blocks
✓ partials/index.html — 3 img tags: added width/height/loading
✓ partials/about.html — 2 img tags: added width/height/loading
```

### Phase 5 — ONE_QUESTION Dialog

For each ONE_QUESTION issue, ask the single question and then immediately fix:

```
One question needed to fix 3 issues:

What is the live URL of this site?
(Used for: canonical tags, sitemap.xml, robots.txt, og:url)
Example: https://example.com
```

After user answers:
1. Add `<link rel="canonical" href="{{url}}{{page_path}}">` template to `header.html`
2. Add `og:url` to Open Graph block in `header.html`
3. Run `bash "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/generate-sitemap.sh" "{{url}}"`

If there are multiple ONE_QUESTION items with different questions, ask them all at once as a numbered list. Never ask the same question twice.

### Phase 6 — DIALOG: Schema

Load `${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/references/seo-knowledge.md` (schema section).

First, check if `docs/product/vision.md` or `docs/product/website-design-brief.md` exist — they may already have the answers. Read them before asking anything.

Then ask only for missing information:

```
For Organization schema I need a few details.
I found from your docs: name="Acme Co", description="..."

Still need:
1. Logo URL (e.g., /images/logo.png or https://example.com/logo.png)
2. Social profiles to list in sameAs (LinkedIn, Twitter/X, GitHub, etc. — paste any you have)

(Press enter to skip any you don't have yet)
```

After answers, write the complete JSON-LD block to `header.html`. Show the exact JSON-LD before writing.

### Phase 7 — DIALOG: Alt Text

For each image with missing or auto-suggested alt text:

```
Alt text needed for 3 images:

1. website/partials/index.html → <img src="/images/hero-dashboard.jpg">
   Suggested: "Hero Dashboard"
   Accept, or type replacement: 

2. website/partials/about.html → <img src="/images/team-photo.jpg">
   Suggested: "Team Photo"
   Accept, or type replacement:

3. website/partials/about.html → <img src="/images/office.jpg">
   Suggested: "Office"
   Accept, or type replacement:
```

Accept blank input as "use suggestion". Apply confirmed alt text with Edit tool.

### Phase 8 — DIALOG: Missing Titles and Descriptions

For each page missing a `<title>` or meta description:

1. Read the source `website/src/{page}.md`
2. Propose a title (max 60 chars) and description (max 155 chars) based on the content
3. Present proposals and ask to confirm or rewrite:

```
Missing SEO copy for 2 pages:

index.md (homepage)
  Title (60 chars max):     "Acme — Project Management for Small Teams"
  Description (155 chars):  "Acme helps small teams ship faster with lightweight project tracking. No clutter, no enterprise bloat."
  Accept both? Or type changes:

about.md
  Title:       "About Acme — Built by a team of former startup founders"
  Description: "The story behind Acme: why we built it, who we are, and what drives us."
  Accept both? Or type changes:
```

On confirmation, update the `title:` and `description:` frontmatter in each `website/src/{page}.md`. After all src edits, invoke `b2:sync-expert` to resync, then rebuild.

### Phase 9 — EXTERNAL Instructions

For each EXTERNAL issue, print exact steps. Do not summarise vaguely — give the user the exact URL and exact action.

```
Things you need to do manually:

⚠ Google Search Console
  1. Go to https://search.google.com/search-console
  2. Add your property: https://example.com
  3. Verify ownership (HTML file method is easiest — I can generate the file if you get the code)
  4. Submit sitemap: https://example.com/sitemap.xml
  Estimated time: 10 minutes

⚠ PageSpeed / Core Web Vitals
  1. Go to https://pagespeed.web.dev/
  2. Enter your URL
  3. Share the LCP and CLS scores with me — I'll fix what's fixable in code
  Estimated time: 2 minutes

⚠ og:image missing
  You don't have a social sharing image yet.
  Ideal: 1200×630px, shows your brand clearly when shared on LinkedIn/X.
  Run /b2:illustrate or /b2:image to create one, then re-run /b2:seo.
```

### Phase 10 — Rebuild and Final Report

Rebuild:
```bash
# If make available:
cd website && make
# Otherwise:
bash "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/assemble.sh"
```

Then print the final report:

```
SEO Fix Complete — Acme

Fixed automatically (8):
  ✓ lang="en" added to <html>
  ✓ viewport meta added
  ✓ font-display: swap added (2 fonts)
  ✓ 6 img tags: width/height/loading added
  ✓ canonical tag template added
  ✓ sitemap.xml generated (5 pages)
  ✓ robots.txt created
  ✓ Organization + WebSite JSON-LD schema added

Fixed with your input (5):
  ✓ Organization schema: name, logo, social links
  ✓ Alt text confirmed on 3 images
  ✓ Title + description added to index.md, about.md

Still needs action (3):
  ⚠ Google Search Console — set up at search.google.com/search-console
  ⚠ PageSpeed score — test at pagespeed.web.dev and share results
  ⚠ og:image — create a 1200×630 social image

Handed off (1):
  → /b2:write — 2 thin pages need more content: posts/intro.md, services.md

Next: Run /b2:serve then /b2:website-review to verify the rebuilt site.
```

---

## Image Optimisation Mode

Triggered by: "images", "webp", "convert images", "image size", "fix images", "loading time", "resize images".

### Step 1 — Audit

Determine the image source directory. Default: `website/src/images/`. Ask if unclear.

Run (Bash):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/prep-images.py" website/src/images/
```

Parse `WOULD_FIX:` lines and report a clean summary:

```
Found 6 images to optimise in website/src/images/:
  hero.jpg          340KB  1920×800   → resize to 1920px + convert to WebP
  team-photo.png    180KB   800×600   → convert to WebP
  logo.png           12KB   400×120   → convert to WebP
  ...
Estimated saving: ~1.4MB
```

If `TOOL:` line shows all tools false, report:
```
No image tools found. Install one:
  pip install Pillow         (recommended — Python, no extra dependencies)
  brew install webp          (cwebp)
  brew install imagemagick
```

Also run (Bash) to check HTML tag issues:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/fix-img-tags.py" audit
```

### Step 2 — Load Design Size Specifications

Read `website/theme/{THEME}/design.md` (Read tool). Look for the `### Image Size Specifications` table. Extract the **Source max-width** column — this is the exact value to pass to `prep-images.py --max-width` for each image role.

Example table structure:
```
| Role       | CSS component              | Source max-width |
|------------|---------------------------|-----------------|
| hero       | .hero                     | 1920            |
| content    | .content-block__image     | 800             |
| card       | .post-list-item__thumb    | 800             |
```

If `design.md` exists and has the table, group source images by their likely role:
- Images with names containing `hero`, `banner`, `cover` → hero role
- Images in posts/, team/, content/ → content role
- Images with names containing `thumb`, `card`, `small` → card role
- All others → default to the largest non-hero source max-width

If `design.md` is missing or has no Image Size Specifications table, ask the user:
```
No image size specs found in design.md. What max-width should I use?
Common values: 1920px (hero/full-bleed), 1200px (content), 800px (cards/thumbs)
Or run /b2:design to regenerate design.md with image specs.
```

### Step 3 — Process Images

Process each group with its design-specified max-width. If all images share one size, one pass is fine:

```bash
# Example — hero images at 1920px:
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/prep-images.py" website/src/images/hero.jpg --fix --max-width 1920

# Example — content images at 800px:
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/prep-images.py" website/src/images/team-photo.jpg --fix --max-width 800
```

For a directory with mixed roles, process the whole directory at the most conservative (smallest) source max-width from the spec table — this is safe. If the user has distinct subfolders per role, process each folder at its spec value.

Parse `CONVERT:`, `RESIZE:`, and `COMPRESS:` lines and report each result. Report the `DONE:summary:` totals.

### Step 4 — Fix Img Tags in Partials

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/fix-img-tags.py" fix
```

### Step 5 — Wrap in `<picture>` for WebP delivery

After conversion, partials referencing `.jpg`/`.png` need `<picture>` wrappers so modern browsers get WebP while older ones fall back gracefully. Read each affected partial, present proposed changes grouped by file, confirm before writing:

```html
<!-- Before -->
<img src="/images/hero.jpg" alt="Hero" width="1920" height="800" loading="eager" fetchpriority="high">

<!-- After -->
<picture>
  <source srcset="/images/hero.webp" type="image/webp">
  <img src="/images/hero.jpg" alt="Hero" width="1920" height="800" loading="eager" fetchpriority="high">
</picture>
```

### Step 6 — CSS/JS Performance Fixes

Apply `font-display: swap` and script placement fixes using Read + Edit.

### Step 7 — Rebuild and Report

Rebuild, then print totals:
```
Image optimisation complete.

Processed: 6 images → website/src/images/
  hero.jpg       340KB → hero.webp      88KB  (saved 252KB, resized 2400→1920px)
  team-photo.png 180KB → team-photo.webp 43KB  (saved 137KB)
  ...
Total saved: 1.9MB

Partials updated: 4 files (using <picture> fallback)
HTML: img width/height/loading attributes fixed on 8 tags

Next: Run /b2:serve then test at https://pagespeed.web.dev/ to verify LCP improvement.
```

---

## Coaching Mode

Triggered when the user asks a question about SEO strategy, not a fix request.

Load `${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/references/seo-knowledge.md`.

Anchor advice to the specific site. Read `docs/product/vision.md` and `docs/product/website-design-brief.md` to understand who the site is for and what it's selling. Do not give generic advice when specific advice is possible.

---

## Handoff Signals

- Thin content pages → suggest `/b2:write` per page
- src file changes made → invoke `b2:sync-expert` skill, then rebuild
- Any dist changes → rebuild and offer `/b2:website-review`
- og:image missing → suggest `/b2:illustrate` or `/b2:image`

---

## Additional Resources

### Reference Files
- **`references/seo-knowledge.md`** — Elite SEO knowledge: ranking signals, schema, content strategy, CWV, entity SEO. Load for coaching mode and schema generation.
- **`references/b2-seo-guide.md`** — b2 file map, fix locations, header template patterns, content inventory commands, schema examples.

### Scripts
- **`scripts/seo-audit.sh`** — HTML audit across `dist/`. Outputs `ISSUE:`/`WARN:`/`OK:` lines for titles, meta, canonical, OG, schema, images, word count.
- **`scripts/generate-sitemap.sh`** — Generates `sitemap.xml` and `robots.txt` in `dist/`. Arg: base URL.
- **`scripts/prep-images.py`** — **Primary image tool.** Resizes (if over `--max-width`) and converts to WebP in one pass. Auto-detects Pillow → cwebp → ImageMagick. Accepts file or directory. Audit (no `--fix`): shows what would happen. Fix: resizes and converts. Flags: `--max-width N`, `--quality N`, `--force`, `--delete-originals`.
- **`scripts/optimize-images.sh`** — Audits image format/size/tag issues and CSS/JS performance. Reports only — does not modify files. Use `prep-images.py --fix` for actual processing.
- **`scripts/fix-img-tags.py`** — Fixes `<img>` tag attributes in partials: adds width/height (from image files), loading, fetchpriority. Modes: `audit`, `fix`, `fix --dry-run`.
