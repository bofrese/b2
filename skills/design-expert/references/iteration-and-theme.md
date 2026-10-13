# Phases D, E - Iteration and Theme Generation

---

## Phase D - Iteration

Update only the chosen concept's HTML file based on feedback. Do not touch the other two.

After each update, regenerate `website/mockups/index.html` (same procedure as Phase C - "Generate the gallery" in `references/mockups.md`) so its thumbnail and design notes reflect the change. The edit is in place: no new concept file is created.

After each update: "I've updated concept-N and refreshed the gallery. Reopen `website/mockups/index.html`. What else needs changing, or are you ready to approve?"

Repeat until the user explicitly approves. Approval trigger words: "approved", "looks great", "go ahead", "ready to generate", "that's it". Do not treat "done" alone as approval - "done with the nav" means feedback, not sign-off.

Update `website/docs/status.md` with the chosen concept number:
```
  phase: iteration
  concept: 2
```

On approval, update:
```
  phase: theme
```

Then proceed directly to Phase E.

---

## Phase E - Theme Generation

**Ask the user for a theme name:**

> "What should we call this theme? This becomes the folder name under `website/theme/`. Default: `b2`"

Use the user's answer (or `b2` if they accept the default) as `{THEME}` for all file paths below.

**Write `website/b2.cfg`** - create or update, preserving any existing keys. Set or replace only the `THEME=` line:

```
THEME={chosen name}
```

(BUILD_TOOL and BASE_PATH are added by `/b2:setup` later.)

All theme files go in `website/theme/{THEME}/`.

**Read `${CLAUDE_PLUGIN_ROOT}/skills/design-expert/references/theme-generation.md`** using the Read tool. It contains the required CSS structure, components.md format, design.md format, and website/docs/decisions.md design language template. Do not generate theme files without reading it.

**Generate 6 files in `website/theme/{THEME}/`** using the approved concept as source of truth:

1. `website/theme/{THEME}/styles.css` - complete CSS (the mockup's full CSS: base + components + all bespoke effects, keyframes, shaders-in-CSS)
2. `website/theme/{THEME}/components.md` - every semantic class used in any mockup, grouped by context
3. `website/theme/{THEME}/header.html` - full document head (carrying **all** of the mockup's CDN library/font links, preconnects, importmaps) + site header with real nav items
4. `website/theme/{THEME}/footer.html` - site footer + the mockup's end-of-body scripts
5. `website/theme/{THEME}/scripts.js` - the chosen mockup's **full** JavaScript (every bespoke animation / interaction / 3D init), plus the base nav toggle, smooth scroll, and footer year. Do NOT reduce it to minimal boilerplate.
6. `website/theme/{THEME}/design.md` - design guide for building new pages in this theme

**Additional theme files (as needed):** vendor any self-hosted library, extra stylesheet, or font the mockup uses as extra `*.js` / `*.css` files in the theme folder - the build copies all theme `*.css`/`*.js` to `dist/`. Put fonts and other binary assets (woff2, glb, mp4, …) under `website/theme/{THEME}/assets/` - the build copies that folder to `dist/`.

**Critical rule for components.md:** Every semantic class used in any HTML section of any html in the theme must be listed in `components.md`. If a class appears in the HTML but not in `components.md`, `/b2:sync` will invent class names.

**Update `website/docs/decisions.md`** with the design language section. Read it first. If it already contains a `## Design Language` section, replace it entirely - do not append a second block. If no such section exists, append it after the existing content. See `references/theme-generation.md` for the format.

**Copy chosen mockup to theme:**

```bash
# Replace N with the actual chosen concept number (1, 2, or 3)
# Replace {THEME} with the theme name chosen above
cp website/mockups/concept-N.html website/theme/{THEME}/mockup.html
```

**Externalise the mockup's assets into the theme - separate the layers, lose nothing.** Read `website/theme/{THEME}/mockup.html`, then rewrite it:
- Move the mockup's **own** `<style>` contents into `styles.css`; replace the block with `<link rel="stylesheet" href="styles.css" />`.
- Move the mockup's **own** inline `<script>` (no `src`) contents into `scripts.js`; replace the block with `<script src="scripts.js"></script>`.
- **KEEP every external `<link>` and `<script src="…">`** (CDN libraries, web fonts, importmaps, module scripts) exactly as written - copy them into `header.html`/`footer.html` too. Never delete them; they are the site's libraries.
- Vendor any self-hosted library/font the mockup references into the theme folder (see "Additional theme files" above) so the build copies it to `dist/`.

The originals in `website/mockups/` remain untouched. `mockup.html` in the theme requires the local server to render correctly.

**Carry brand assets into the theme.** If `website/mockups/assets/` contains any user-provided assets (logo, images, illustrations):

```bash
if [ -d website/mockups/assets ] && [ -n "$(ls -A website/mockups/assets 2>/dev/null)" ]; then
  mkdir -p "website/theme/{THEME}/assets"
  cp -R website/mockups/assets/. "website/theme/{THEME}/assets/"
fi
```

Then rewrite asset references in the theme files (`mockup.html`, `styles.css`, `header.html`, `footer.html`) from the mockup-relative `assets/<file>` to the site-absolute `/assets/<file>` - the build copies `theme/{THEME}/assets/` to `dist/assets/`, so `/assets/<file>` resolves on the live site. (Both the design mockups and the live pages then use the same real assets.)

**Update `website/docs/status.md`:**
```
- [x] Design → website/theme/{THEME}/
```

Tell the user:
```
Theme generated in website/theme/{THEME}/ (styles.css, components.md, header.html, footer.html,
scripts.js, design.md, mockup.html - plus any vendored libraries/fonts/assets the design uses).
Run /b2:sync to convert your content files, then /b2:setup to configure the build.
```

**Redesign (existing partials present).** If `website/partials/` already has content from a previous theme, the theme swap changes the class vocabulary, but `/b2:sync`'s stale-detection keys off `.md` mtime and will not notice. Tell the user to re-sync with partials re-evaluation, and note the redesign delta from `components.md` so sync knows what changed:
```
This is a redesign - your existing pages use the old theme's classes. Run /b2:sync and it will
re-evaluate every partial against the new components.md: partials whose classes still exist are kept
(surgically), partials using renamed/dropped classes are redone. Reused classes mean most pages carry
over untouched.
```
(Sync handles this per "Handling Existing Partials" → "Redesign" in its conversion guide.)

Then ask: "Shall I run /b2:build now to assemble dist/ so you can preview with /b2:serve? (yes/no)"

If yes: use the Skill tool to invoke `b2:build-expert`. On a redesign (existing partials re-themed), build-expert's new-page heuristic won't catch pages that already existed under the old theme - after build completes, also say: "Redesigned pages won't automatically get flagged for review since they aren't new. Run `/b2:website-review` to check they live up to the new theme's mockup, not just its class names."
If no: "Run /b2:build when you're ready to preview."
