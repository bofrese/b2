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
   - `pagespeed` / `cwv` / `lighthouse` → **PageSpeed Check Mode**
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

**Font CDN check** — don't grep for one provider; run the detector, which checks every external stylesheet link, not just Google Fonts (Bash):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/selfhost-fonts.py" audit
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
- Any font CDN detected (Google Fonts, Fontshare, or others — check every `<link rel="stylesheet">` pointing off-domain, not just the first one found) → self-host using `selfhost-fonts.py fix` (see `references/b2-seo-guide.md`) — it detects and patches all of them in one pass, including header.html directly
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
- No backlinks (strategy advice only)
- og:image missing AND no page images exist (no source to crop — must create with `/b2:illustrate`)

**HANDOFF issue** (automatable, but needs the live site — not part of Full Fix Mode's local-dist phases):
- PageSpeed/Core Web Vitals — see "PageSpeed Check Mode" below. Mention it in the plan (see Phase 3) rather than treating it as EXTERNAL busywork; it only requires the user to confirm publishing, not to run anything manually.

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

HANDOFF: N issues
  → 2 thin pages — run /b2:write to rewrite them
  → PageSpeed/Core Web Vitals — run `/b2:seo pagespeed` once this is published (I run the test myself, no manual steps)

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

Check `website/b2.cfg` for `SITE_URL=` first — `/b2:setup` collects this at project setup, and the build already injects it into canonical/og:url on every page. Only ask if it's genuinely missing (older project, setup skipped, or left blank at the time).

```
One question needed to fix 3 issues:

What is the live URL of this site?
(Used for: canonical tags, sitemap.xml, robots.txt, og:url)
Example: https://example.com
```

After user answers:
1. Write `SITE_URL={value}` into `website/b2.cfg` (add the line if absent)
2. Rebuild (`make` or `bash scripts/assemble.sh`) so canonical/og:url are injected across all pages
3. Run `bash "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/generate-sitemap.sh" "{{url}}"`

Do not patch `header.html` directly — canonical/og:url are `{{CANONICAL}}` placeholders filled by the assembler from `b2.cfg`, not static text to edit per project.

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

Still needs action (2):
  ⚠ Google Search Console — set up at search.google.com/search-console
  ⚠ og:image — create a 1200×630 social image

Handed off (2):
  → /b2:write — 2 thin pages need more content: posts/intro.md, services.md
  → Run `/b2:seo pagespeed` once this build is published to check Core Web Vitals

Next: Run /b2:serve then /b2:website-review to verify the rebuilt site.
```

---

## PageSpeed Check Mode

Triggered by: "pagespeed", "core web vitals", "cwv", "lighthouse", "test performance", `/b2:seo pagespeed`. Also reachable as the natural next step after Full Fix Mode rebuilds the site.

PageSpeed Insights tests a live URL over the network — it cannot see `website/dist/` directly. Every step below exists because of that one constraint.

### Step 1 — Confirm SITE_URL

Read `website/b2.cfg` for `SITE_URL=`. If missing or empty, ask for it and offer to save it to `b2.cfg` (see `setup-expert` Step 2b for the convention) — do not proceed without it.

### Step 2 — Confirm the Build Is Published

Ask the user directly: "Has the current build been published to {SITE_URL}? PageSpeed tests the live site, not your local `dist/` — I need to know it's current before testing." **Never publish automatically** — this is the user's call every time, even if they said yes last time.

- If not published: stop here. Tell them to publish (`make publish`, or their project's publish path) and run this again.
- If published: continue.

### Step 3 — Check for an API Key

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/check-pagespeed-key.py"
```

If `MISSING`: load `references/pagespeed-api-key.md` and follow it (explain the free-key setup, save to `.env` if the user pastes one). The check without a key still works but often hits an already-exhausted shared quota — try it anyway if the user declines to get a key, and surface the quota error plainly if it happens.

### Step 4 — Run the Check

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/pagespeed-check.py" "{SITE_URL}" --strategy mobile
python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/pagespeed-check.py" "{SITE_URL}" --strategy desktop
```

Run both — mobile and desktop scores commonly diverge (mobile is CPU/network-throttled in Lighthouse; a healthy desktop score alongside a poor mobile score usually points at render-blocking CDN resources, not a fundamental site problem).

Parse the `METRIC:`/`FIELD_METRIC:`/`OPPORTUNITY:`/`DIAGNOSTIC:` lines. `POOR`/`NEEDS_IMPROVEMENT` metrics and top `OPPORTUNITY` lines are what to act on; `DIAGNOSTIC` lines are secondary.

### Step 5 — Map Findings to Fixes

Known automated fixes already in this skill — apply directly, don't just report:

| Finding | Fix |
|---|---|
| Poor LCP/FCP + `render-blocking-resources`/`BLOCKING_RESOURCE:` + any font CDN in header | `scripts/selfhost-fonts.py fix` — detects every font CDN (not just Google Fonts), patches header.html and styles.css directly, no manual follow-up edit needed |
| Poor LCP with `LCP_PHASE:Element render delay` dominating over `LCP_PHASE:Time to first byte` | Not a resource-loading problem — something on the main thread is delaying paint (decorative JS, heavy animation init). Check `LCP_ELEMENT:` to see what's actually the LCP candidate (can be text, not an image). Fix is to defer non-critical JS via `requestIdleCallback`, not to remove the effect — see "sequence, don't cut" below |
| Poor LCP, no `<link rel="preload">` for the hero image | Confirmed already handled by `assemble.sh`/`assemble-page.sh`'s `{{LCP_PRELOAD}}` injection — check the hero `<img>` has `fetchpriority="high"` (`fix-img-tags.py fix` if not) |
| CLS + missing image dimensions | `scripts/fix-img-tags.py fix` |
| `unminified-css`/`unminified-javascript` opportunities | Theme CSS/JS should already be minified on copy to `dist/` — see `scripts/minify-css.py`/`minify-js.py`, wired into `build-expert`'s `assemble.sh` and (for projects with their own Makefile) `website/scripts/minify-*.py`. If the opportunity still appears, the project's build isn't calling them yet — wire it in, don't hand-minify inline. |
| `unused-css-rules`/`unused-javascript` | Report only — requires design judgement about what to cut |
| Accessibility `color-contrast` diagnostic | DIALOG — propose specific color adjustments in `styles.css`, confirm with user before applying (visual/brand decision) |

For anything with no automated fix, report it plainly rather than silently skipping — the user decides whether it's worth hand-fixing.

### Step 6 — Rebuild and Report

If any fix was applied, rebuild (`make` or `scripts/assemble.sh`), then report:

```
PageSpeed Check — Acme (https://example.com)

Mobile: Performance 77 → Accessibility 96 → Best Practices 100 → SEO 100
  LCP 4.1s (POOR)  FCP 3.3s (POOR)  CLS 0.00 (GOOD)  TBT 0ms (GOOD)

Desktop: Performance 99 (all GOOD)

Fixed:
  ✓ Self-hosted Inter + JetBrains Mono (removed Google Fonts CDN round-trip)

Reported, not auto-fixed:
  → Minify CSS (3KB) / JS (2KB) — no automated tool for this yet
  → color-contrast — needs a design decision, propose specific values if you want this fixed

Next: Publish this build, then run `/b2:seo pagespeed` again to confirm the mobile LCP/FCP numbers improved.
```

Close by asking the user to publish again — never do it automatically — and offer to re-run the check once they confirm.

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
- **`references/pagespeed-api-key.md`** — Guided setup when `check-pagespeed-key.py` returns `MISSING`.

### Scripts
- **`scripts/seo-audit.sh`** — HTML audit across `dist/`. Outputs `ISSUE:`/`WARN:`/`OK:` lines for titles, meta, canonical, OG, schema, images, word count.
- **`scripts/generate-sitemap.sh`** — Generates `sitemap.xml` and `robots.txt` in `dist/`. Arg: base URL.
- **`scripts/pagespeed-check.py`** — Calls the PageSpeed Insights API for a live URL (no browser automation). Outputs `SCORE:`/`METRIC:`/`FIELD_METRIC:`/`LCP_ELEMENT:`/`LCP_PHASE:`/`BLOCKING_RESOURCE:`/`OPPORTUNITY:`/`DIAGNOSTIC:` lines. Args: `<url> [--strategy mobile|desktop] [--categories ...]`.
- **`scripts/selfhost-fonts.py`** — Detects every external font-CDN stylesheet in header.html (provider-agnostic — any CDN serving `@font-face` CSS, not just Google Fonts), downloads the files, patches styles.css and header.html directly. Modes: `audit`, `fix`.
- **`scripts/check-pagespeed-key.py`** — Checks for a PageSpeed API key in `.env`/env vars. Prints `OK:<source>` or `MISSING`, exit code 0/1.
- **`scripts/prep-images.py`** — **Primary image tool.** Resizes (if over `--max-width`) and converts to WebP in one pass. Auto-detects Pillow → cwebp → ImageMagick. Accepts file or directory. Audit (no `--fix`): shows what would happen. Fix: resizes and converts. Flags: `--max-width N`, `--quality N`, `--force`, `--delete-originals`.
- **`scripts/optimize-images.sh`** — Audits image format/size/tag issues and CSS/JS performance. Reports only — does not modify files. Use `prep-images.py --fix` for actual processing.
- **`scripts/fix-img-tags.py`** — Fixes `<img>` tag attributes in partials: adds width/height (from image files), loading, fetchpriority. Modes: `audit`, `fix`, `fix --dry-run`.
- **`scripts/minify-css.py`** — Pure-Python CSS minifier (comments + whitespace), no Node/npm dependency. Wired into the build, not a manual step.
- **`scripts/minify-js.py`** — Conservative JS minifier: strips only full-line comments (never mid-line, to avoid misreading regex literals), preserves all whitespace/newlines otherwise. Deliberately not a full minifier — see its docstring for why.
