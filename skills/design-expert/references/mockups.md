# Phase C — Three Mockup Concepts

Before launching agents, read `docs/product/website-design-brief.md` (guaranteed to exist — the Prerequisite Check resolved or created it; **never** fall back to `design-brief.md`, which is a different scope) and `website/docs/content-types.md` in full. Read `website/docs/status.md` to retrieve the three confirmed directions from Phase B2. Paste all of this into each agent prompt verbatim.

Ensure the output directory exists:

```bash
root="$(pwd)" && mkdir -p "$root/website/mockups/assets"
```

(The `assets/` subfolder holds any real images/illustrations/logos a mockup links to. The mockups folder is served during review, so linked assets resolve over http.)

**Optional knowledge slice.** If a confirmed direction calls for motion, 3D, or a specific design-system approach, read the relevant file from `${CLAUDE_PLUGIN_ROOT}/shared/design/` (`animation-motion.md`, `3d-visual-effects.md`, `design-systems.md` — see `shared/design/README.md`) and paste the pertinent lines into that agent's prompt under a `DESIGN KNOWLEDGE` block. Do not load slices a direction does not need.

**Available assets.** List real brand assets the user provided (from Phase A1):

```bash
ls website/mockups/assets/ 2>/dev/null
```

If any exist, pass their filenames into every agent prompt (the `AVAILABLE ASSETS` block below) so concepts use the real logo/images/illustrations via relative `assets/…` URLs instead of placeholders. If the folder is empty, agents use Lucide placeholders.

**Redesign — existing class vocabulary.** If a current theme exists (read `THEME` from `website/b2.cfg`, then check `website/theme/{THEME}/components.md`), this is a redesign of a live site. Read that `components.md` and pass its class list into every agent prompt (the `EXISTING VOCABULARY` block below). The goal: reuse the same semantic class names **where the new design has an equivalent element**, so existing partials keep working and the theme can be swapped without rewriting every page. This is a soft suggestion, **not** a constraint — never contort a stunning new design to fit old names. If the folder/file doesn't exist, this is a first design; omit the block.

Launch 3 agents **simultaneously** using the Agent tool with `run_in_background: true`. Each writes one concept file in complete isolation — they must not share context or see each other's output. Give each the specific direction confirmed in Phase B2 — use the exact name and description from `website/docs/status.md`.

**Construct each agent prompt with these blocks in order:**

```
You are an award-winning web designer generating a standalone HTML mockup.

Write a single self-contained HTML file to: [CONCEPT PATH]

Design direction for this concept: [DIRECTION HINT]

Use the confirmed direction name and its interpretation from the Phase B2 status entry.
Translate it into concrete HTML/CSS decisions — layout logic, typographic hierarchy,
spatial approach, colour application. Make it feel specific to this direction, not generic.

---
DESIGN BRIEF (source of truth — palette, typography, principles):

[PASTE FULL CONTENT OF docs/product/website-design-brief.md]

---
SITE STRUCTURE (use real nav items and content types from this):

[PASTE FULL CONTENT OF website/docs/content-types.md, or write "Not available — use placeholder nav" if missing]

---
AVAILABLE ASSETS (real brand assets — reference via relative assets/<file> URLs):

[LIST each file in website/mockups/assets/ with what it is, e.g. "assets/logo.svg — company logo",
"assets/hero.jpg — hero photo". Use these instead of placeholders where they fit. If none, write
"None provided — use Lucide placeholders for imagery."]

---
EXISTING VOCABULARY (redesign only — SOFT reuse hint, not a constraint):

[PASTE the class list from the current website/theme/{THEME}/components.md, or OMIT this whole block
on a first design.]

If present: reuse these semantic class names where your design has an equivalent element (a hero is
still `.hero`, primary nav is still `.site-nav`, a post card is still `.post-card`) so the site's
existing pages flow into your design with minimal rework. Add new class names freely for genuinely new
structure, and do NOT bend the design to fit an old name that no longer makes sense. Reuse where it's
natural; invent where it's better.

---
MOCKUP REQUIREMENTS:

1. FULL CREATIVE FREEDOM — go all out. Make this the most stunning, modern expression of the direction.
   Use whatever it takes: any CSS technique, any web-font provider, and any JavaScript / animation / 3D
   library loaded from a reputable CDN (GSAP + ScrollTrigger, Motion, anime.js, Three.js / React Three
   Fiber via importmap, Spline, Lenis, WebGL/GLSL shaders, canvas, native View Transitions, scroll-driven
   CSS, video, Lottie, …). See the DESIGN KNOWLEDGE block above for current, version-checked options.
   There is no dependency whitelist — reach for whatever delivers the vision.
2. Put your OWN CSS in a <style> block in <head> (so Phase E can extract it into the theme), and your
   OWN JS in a <script> block before </body>. You MAY additionally link external CSS/JS libraries and
   fonts via CDN in <head> — those links are carried into the production theme verbatim.
3. Use semantic BEM-style class names for the CONTENT STRUCTURE (.hero, .hero__title, .post-card,
   .post-card__meta) — these become the production theme's component vocabulary, so name them
   descriptively. Bespoke decorative / animation / effect layers can be named and structured however
   the effect needs (IDs as JS hooks, canvas mounts, wrappers) — only the reusable content structure
   must stay semantic.
4. Assets: link real images / illustrations / logos with relative URLs under `assets/` (i.e.
   `website/mockups/assets/…`). The mockups folder is served during review, so linked assets resolve.
   Where you have no real asset, use Lucide placeholders via CDN
   (`<script src="https://unpkg.com/lucide@latest"></script>`, styled placeholder divs with
   `<i data-lucide="image"></i>`, `lucide.createIcons()` before `</body>`).
5. Include all of these sections:
   - Full site header with real nav items (from site structure above)
   - Hero / landing section
   - One representative section per content type
   - One index/listing section per content type marked Index: yes
   - Site footer
6. The file must be visually complete — a stakeholder evaluates the full design direction from this file alone.
7. This concept must look VISUALLY DISTINCT from the other two directions — different layout logic,
   different typographic hierarchy, different spatial approach. Colour variations alone are not enough.
8. Immediately after the opening <body> tag, include a design-notes comment block the gallery will
   extract, in exactly this form:
     <!-- Design notes: 1-2 sentences on this direction's key design decisions -->
9. Quality bar: prefer native (CSS/WAAPI/View Transitions/scroll-driven) before a library, but never
   hold back when a library delivers the vision. Gate all motion behind `prefers-reduced-motion`,
   lazy-load heavy 3D/media with a static fallback, and keep focus states, alt text, and contrast intact.

Write only the HTML file (a single .html per concept — it may reference CDN libraries and served
assets). Do not summarise or explain.
```

**Concept paths:**
- Concept 1: `website/mockups/concept-1.html`
- Concept 2: `website/mockups/concept-2.html`
- Concept 3: `website/mockups/concept-3.html`

**Wait for all 3 agents to complete** before replying to the user.

### Generate the gallery

Build `website/mockups/index.html` from `${CLAUDE_PLUGIN_ROOT}/shared/design/gallery-template.html`:

1. Read the template.
2. Replace `{{GALLERY_TITLE}}` (site/theme name) and `{{COUNT}}` (number of concepts).
3. Replace the `<!-- CARDS -->` marker with one `.card` block per concept, **in creation order** (concept-1, concept-2, concept-3). For each card:
   - `iframe src` and both `href`s point to that `concept-N.html`.
   - `<h2>` = the direction name from Phase B2; `.direction` = "Concept N".
   - `.notes` = the text from that concept's `<!-- Design notes: … -->` block (read each concept file to extract it). If the block is missing or empty, fall back to the direction name so the card never renders blank.
4. Write `website/mockups/index.html`. The gallery shell is self-contained; the mockups it embeds may load CDN libraries and linked assets, so review it through the local web server when a mockup links local assets (CDN-only mockups also work on `file://`).

Then offer to serve and tell the user:
```
Three concepts ready. Review them side by side in the gallery:

  website/mockups/index.html

Because the mockups may use linked assets and libraries, view via the local server:
run /b2:serve (or your own static server on website/) and open /mockups/index.html.

Which concept do you want to develop further?
```

Use the actual direction names from Phase B2. Do NOT use `open` with a file path.

Update `website/docs/status.md`:
```
  phase: iteration
```

**Wait for the user to name a concept before proceeding.** Do not advance automatically.

Then load `references/iteration-and-theme.md` and continue with Phase D.
