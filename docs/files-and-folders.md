# Files and Folders
*Last verified: 2026-07-16*

Everything below is created **in your project**, not inside the plugin. Only `b2/` (this plugin's own code) is installed by Claude Code — everything in this document is output the plugin writes into the project you run it in.

## Top-Level Layout

```
docs/
  notes/              ← /b2:talk captures (README.md + category files)
  product/            ← vision.md, website-design-brief.md, illustration-style.md
  presentations/       ← /b2:present output

ai/
  illustrations.md     ← /b2:illustrate session log

website/
  docs/
    status.md           ← phase-completion tracker, read by /b2 for routing
    decisions.md         ← brand voice guide, read by every AI-driven command
    content-types.md    ← page type definitions, from /b2:structure
  src/                  ← your markdown content (human-authored, source of truth)
  partials/             ← AI-generated semantic HTML (never edit by hand)
  theme/{name}/         ← visual layer: CSS, components, header/footer, scripts
  mockups/              ← /b2:design's three concepts + gallery, pre-theme
  dist/                 ← assembled, deployable output (never edit by hand)
  b2.cfg                ← THEME, BUILD_TOOL, BASE_PATH
  Makefile, docker-compose.yml, websync.cfg  ← only if build tooling was generated

.env                    ← GEMINI_API_KEY, user-created, should be gitignored
.playwright-mcp/        ← /b2:website-review screenshots
```

## Content Pipeline

Three representations of the same page, in increasing specificity:

```
website/src/page.md            human-authored content, source of truth
    ↓  /b2:sync (AI step)
website/partials/page.html      semantic HTML body only — no <html>, no header/footer
    ↓  make / assemble script
website/dist/page.html           assembled: header + partial + footer + theme assets
```

`partials/*.html` files use **semantic class names only** — what something is (`.hero`, `.post-header`), never how it looks (no `.blue-bg`, no `.large-text`). All visual styling lives in `theme/{name}/styles.css`, keyed to those same class names. This separation is what lets `/b2:design` regenerate a theme without touching a word of content.

`theme/{name}/components.md` is the contract enforcing that separation: it's the list of semantic classes `/b2:sync` is allowed to use. A class must exist in both `components.md` and `styles.css` — one without the other means `/b2:sync` can't use it, or `styles.css` has dead CSS.

## Global File Map

| File / folder | Created by | Read by |
|---|---|---|
| `docs/notes/README.md`, `docs/notes/{category}.md` | `/b2:talk` | `/b2:vision`, `/b2:brand`, `/b2:structure`, `/b2:write` |
| `docs/product/vision.md` | `/b2:vision` | `/b2:brand`, `/b2:structure`, `/b2:write`, `/b2:design`, `/b2:illustrate` |
| `docs/product/website-design-brief.md` | `/b2:brand` (or a thin wrapper from `/b2:design` if missing) | `/b2:structure`, `/b2:design`, `/b2:write`, `/b2:illustrate` |
| `docs/product/illustration-style.md` | `/b2:illustrate` (first run / style updates) | `/b2:illustrate` (every run) |
| `website/docs/decisions.md` | `/b2:brand` | `/b2:design`, `/b2:sync`, `/b2:write`, `/b2:website-review`, `/b2:illustrate` |
| `website/docs/status.md` | `/b2:vision` (creates); every skill updates | `/b2` (routing); every skill (phase detection) |
| `website/docs/illustrations.md` | `/b2:illustrate` | reference only |
| `website/docs/content-types.md` | `/b2:structure` | `/b2:sync`, `/b2:design`, `/b2:write` |
| `website/src/*.md` | `/b2:write` (+ stub files from `/b2:structure`) | `/b2:sync` |
| `website/src/images/*.png` | `/b2:image` (API) or manually via the `/b2:illustrate` flow | site content |
| `website/mockups/concept-N.html`, `index.html` | `/b2:design` Phase C/D | your review, before a theme is chosen |
| `website/mockups/assets/` | you, if offered during `/b2:design` | copied into `theme/{name}/assets/` on theme generation |
| `website/theme/{name}/mockup.html` | `/b2:design` (copy of the chosen concept, CSS/JS stripped) | `/b2:sync`, `/b2:website-review` |
| `website/theme/{name}/styles.css`, `header.html`, `footer.html`, `scripts.js`, `design.md` | `/b2:design` | build step, `/b2:sync`, `/b2:website-review`, `/b2:illustrate` |
| `website/theme/{name}/components.md` | `/b2:design` | `/b2:sync`, `/b2:website-review`, `/b2:setup` |
| `website/partials/*.html` | `/b2:sync` | build step |
| `website/b2.cfg` | `/b2:design` (`THEME=`); `/b2:setup` (adds `BUILD_TOOL=`, `BASE_PATH=`) | every build/serve/review command |
| `website/dist/` | build step (via `/b2:build` or `/b2:setup`) | `/b2:serve`, `/b2:website-review` |
| `website/dist/sitemap.xml`, `robots.txt` | `/b2:seo` | hosting, search engines |
| `.env` | you | `/b2:image`, `/b2:illustrate` (API key) |
| `.playwright-mcp/*.png` | `/b2:website-review` | your review |
| `docs/presentations/{slug}.md` | `/b2:present` | Obsidian Advanced Slides |

## Never Hand-Edit

- `website/partials/*.html` — regenerated by `/b2:sync`; edits will be lost or fought on next sync.
- `website/dist/` — fully regenerated by the build step every time.
- `website/theme/{name}/components.md` — maintained by `/b2:design`/`/b2:sync`; hand-editing breaks the contract with `styles.css`.

## Safe to Hand-Edit

- `website/src/*.md` — this is the actual source of truth for content.
- `website/theme/{name}/styles.css`, `scripts.js` — yours to tune, as long as class names stay in sync with `components.md`.
