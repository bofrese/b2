# Theme Generation Reference

Detailed instructions for Phase E of the design-expert workflow.

---

## styles.css

Generate a complete CSS file covering all semantic components. Organise into sections:

```css
/* ============================================================
   B2 Theme — [Theme Name]
   Generated: YYYY-MM-DD
   ============================================================ */

/* === Reset & Base =========================================== */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: ...; }

/* === Fonts — MUST include font-display: swap =============== */
/* font-display: swap is required for Core Web Vitals (LCP).  */
/* Google Fonts ?display=swap handles this when using their   */
/* CDN — include it in the <link> URL in header.html.         */
/* For self-hosted fonts, declare explicitly:                 */
/*                                                            */
/* @font-face {                                               */
/*   font-family: 'MyFont';                                   */
/*   src: url('/fonts/myfont.woff2') format('woff2');         */
/*   font-display: swap;   ← required                        */
/* }                                                          */

/* === Images — prevent CLS (layout shift) =================== */
/* All <img> elements must have width + height attributes set  */
/* in the HTML. This CSS ensures they behave correctly even    */
/* when those attributes are present.                         */
img {
  max-width: 100%;
  height: auto;       /* overrides the HTML height on small screens */
  display: block;     /* removes inline baseline gap */
}

/* === Typography ============================================= */
h1, h2, h3 { ... }
p { ... }

/* === Layout ================================================= */
.container { ... }
.section { ... }

/* === Shared Components ====================================== */
/* Components used across multiple content types */
.hero { ... }                /* Full-height hero — entry point pages only */
.page-hero { ... }           /* Compact dark hero — destination pages (docs, about, etc.) */
.page-hero__inner { ... }
.page-hero__eyebrow { ... }
.page-hero__title { ... }
.page-hero__subtitle { ... }
.cta { ... }
.btn { ... }
/* etc */

/* === Navigation ============================================= */
.site-nav { ... }
.site-nav__list { ... }
.site-nav__item { ... }
/* etc */

/* === Page Type: post ======================================= */
.post-header { ... }
.post-body { ... }
.tag-list { ... }
/* etc */

/* === Post Index ============================================= */
.post-listing { ... }
.post-list-item { ... }
/* etc */

/* === Page Type: product ==================================== */
/* (if applicable) */

/* === Footer ================================================= */
.site-footer { ... }

/* === Responsive ============================================= */
@media (max-width: 768px) { ... }
```

The **reusable component vocabulary** (the classes content partials will use) must be semantic class names defined in components.md — this is the theme↔content contract. Beyond that, use whatever CSS the design needs: `@keyframes`, custom properties, `@supports`, container queries, complex selectors, pseudo-elements, and IDs as animation/JS hooks for bespoke one-off effects are all fine. Do not flatten the mockup's bespoke CSS to fit a "semantic classes only" rule — carry it in full. Ensure mobile-responsive layout and gate motion behind `prefers-reduced-motion`.

**Shared token classes for repeated content patterns.** If the design has more than one component that displays the same *kind* of content (e.g. any component showing commands/code: a terminal window, a process/timeline step list, inline code in prose), define the colour/style tokens for that content once as small reusable classes (e.g. `.cmd`, `.prompt`, `.comment` for a command-output convention) rather than re-declaring the same colours scoped separately under each component (`.terminal__body .cmd`, `.process__commands .cmd`, …). Scoped-per-component duplicates drift out of sync when one gets tweaked later and the others don't — the whole point of a design system is that "a command looks like a command" everywhere it appears.

**Selector scoping for decorative sibling groups.** When a component has a small fixed set of purely decorative repeated elements sharing a parent with a non-decorative element (e.g. status dots next to a text label, bullet icons next to a caption), give the decorative elements their own class and style that — never a bare tag selector like `.parent span` or `.parent > *`. A bare selector silently catches the sibling label too if it happens to use the same tag, visibly breaking it (e.g. squashing a text label into a tiny circle because it inherited `width/height/border-radius` meant for dots).

---

## components.md

Enumerate every semantic class used in the chosen mockup (across all theme HTML files). Group by context:

**Redesign (a previous `components.md` existed):** the mockups were already generated with the old vocabulary as a soft reuse hint, so keep names identical wherever a component maps 1:1 to the old one (`.hero`, `.site-nav`, `.post-card`, `.content-block`…) — this lets existing partials survive the theme swap. Only rename or drop a class when the new design genuinely changes that component's structure, and add new classes for new structure. At the end of the file, note the delta so the next sync knows what to re-evaluate:

```markdown
## Redesign delta (vs previous theme)
- Reused: .hero, .site-nav, .post-card, .content-block, …
- New: .feature-marquee, .webgl-hero, …
- Dropped/renamed: .old-banner → .page-hero, .sidebar (removed)
```


```markdown
# B2 Theme Components

## Shared
Classes used across multiple content types or in global layout.

| Class | Usage |
|-------|-------|
| `.container` | Page-width wrapper |
| `.section` | Vertical spacing block |
| `.hero` | Full-width hero section |
| `.cta` | Call-to-action block |
| `.btn` | Button element |
| `.btn--primary` | Primary action button |
| `.btn--secondary` | Secondary action button |

## Navigation
| Class | Usage |
|-------|-------|
| `.site-nav` | Site-wide navigation wrapper |
| `.site-nav__list` | Nav item list |
| `.site-nav__item` | Individual nav item |
| `.site-nav__link` | Nav link |
| `.site-nav--open` | State class — nav open on mobile |

## Page (root-level one-off pages)

**Entry points** (index, home, landing): use `.hero` + mascot panel.

**Destination pages** (about, docs, contact, etc.): use `.page-hero` as the intro section — compact dark-background header with eyebrow, h1, and subtitle. No mascot. Then `.content-block` / `.content-block--alt` alternating sections.

`page-hero` is REQUIRED in the components table and CSS — even if no mockup explicitly shows it. It is always needed for destination pages.

| Class | Usage |
|-------|-------|
| `.page-hero` | Compact dark-bg intro — destination pages only |
| `.page-hero__inner` | Max-width container inside page-hero |
| `.page-hero__eyebrow` | Orange pill label (page name) |
| `.page-hero__title` | Bold white h1; `em` renders in accent colour |
| `.page-hero__subtitle` | Muted white one-sentence subtitle |
| `.content-block` | Alternating prose section |
| `.content-block--alt` | Alt background variant (full-bleed) |
| `.content-block__inner` | Inner container for full-bleed alt sections |
| `.content-block__heading` | Section heading (h2) |
| `.content-block__body` | Prose body; max-width ~680px; h3/pre/code styled here |
| ... | (add any additional page classes from the mockup) |

## Post (blog post items)
| Class | Usage |
|-------|-------|
| `.post-header` | Post title + meta block |
| `.post-body` | Post prose content |
| `.tag-list` | Tag list container |
| `.tag` | Individual tag |
| ... | ... |

## Post Index (post listing page)
| Class | Usage |
|-------|-------|
| `.post-listing` | Listing page wrapper |
| `.post-list-item` | Individual post in listing |
| ... | ... |
```

**Completeness rule:** If a class is in any mockup HTML or theme file but not in this table, `/b2:sync` will not know it exists and may invent alternatives. Audit all HTML after generating theme files.

**SEO rule:** The `components.md` table must note which components carry H1 (`.hero`, `.page-hero`) — each should render exactly one `<h1>` per page. The `sync-expert` skill uses this as a constraint when generating partials.

---

## header.html

`header.html` is the full HTML document open — not just a navigation fragment. It must contain the complete `<head>` block and open `<body>`, then the `<header>` element. The Makefile assembles pages as:

```
cat header.html partials/page.html footer.html > dist/page.html
```

So the assembled `dist/*.html` files are only valid HTML if `header.html` opens the document and `footer.html` closes it.

**Required structure — include the full SEO block:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- ═══ SEO — Core ══════════════════════════════════════════ -->
  <!-- NOTE: title and description are site defaults.           -->
  <!-- Page-specific values: add title:/description: frontmatter -->
  <!-- to src/*.md, then run /b2:seo to inject per-page meta.  -->
  <title>[Site Name] — [Tagline]</title>
  <meta name="description" content="[One-sentence site description — what it does, for whom.]" />
  <link rel="canonical" href="[https://yourdomain.com]/" />

  <!-- ═══ SEO — Open Graph (social sharing) ══════════════════ -->
  <meta property="og:type"        content="website" />
  <meta property="og:site_name"   content="[Site Name]" />
  <meta property="og:title"       content="[Site Name] — [Tagline]" />
  <meta property="og:description" content="[One-sentence site description.]" />
  <meta property="og:url"         content="[https://yourdomain.com]/" />
  <meta property="og:image"       content="[https://yourdomain.com/images/og-image.png]" />
  <meta name="twitter:card"       content="summary_large_image" />

  <!-- ═══ SEO — Structured Data (JSON-LD) ════════════════════ -->
  <!-- Update name, url, logo, and sameAs before going live.   -->
  <!-- Run /b2:seo schema to fill these from your brand docs.  -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "name": "[Site Name]",
        "url": "[https://yourdomain.com]",
        "logo": "[https://yourdomain.com/images/logo.png]",
        "sameAs": []
      },
      {
        "@type": "WebSite",
        "name": "[Site Name]",
        "url": "[https://yourdomain.com]"
      }
    ]
  }
  </script>

  <!-- ═══ Fonts, Libraries & Styles ═══════════════════════════ -->
  <!-- Carry EVERY head resource the chosen mockup used, verbatim: web-font links (any provider),
       CDN library <script> / <link> tags (GSAP, Three.js, Motion, Lottie, …), importmaps, module
       preloads, preconnects. This is what makes the live site support any library/font/style. -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=[Fonts]&display=swap" rel="stylesheet" />
  <!-- Example CDN libraries — include whichever the mockup uses, plus any icon library: -->
  <!-- <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script> -->
  <!-- <script src="https://unpkg.com/lucide@latest"></script> -->
  <!-- Self-hosted libraries: vendor into the theme folder and load them here, e.g.
       <script src="/three.module.js" type="module"></script> -->
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
<header class="site-header">
  <!-- nav here — see URL rules below -->
</header>
<main><!-- closed in footer.html — required semantic landmark for SEO and accessibility -->
```

**SEO notes for header.html:**
- All bracketed `[values]` must be replaced with real content — never leave placeholder text in production.
- The title and description here are site-wide defaults. Page-specific values require either: (a) the assembly script injecting frontmatter values, or (b) running `/b2:seo` to update per-page meta after content is written.
- `og:image` should be a 1200×630px image showing the brand clearly — create one with `/b2:image` or `/b2:illustrate`.
- After going live, run `/b2:seo` to fill in canonical URLs, update schema values, and audit every page.

**URL rules for nav links:**

The b2 build produces **flat `.html` files** at `dist/`. Apache httpd (the Docker server) does not auto-append `.html` to extensionless URLs. Nav links must therefore include the `.html` extension for all pages except:
- `/` — maps to `dist/index.html` by default (Apache DirectoryIndex)
- Anchor links (`#section`) — unchanged

| Page | Correct link | Wrong |
|------|-------------|-------|
| Home | `/` | n/a |
| About | `/about.html` | `/about` |
| Docs | `/docs.html` | `/docs` |
| Showcase | `/showcase.html` | `/showcase` |
| How It Works | `/how-it-works.html` | `/how-it-works` |

Read `website/docs/content-types.md` to determine the actual page list and derive correct hrefs. Each `src/*.md` file maps to `dist/*.html` and needs a `.html` href in the nav.

**Do not hardcode an active-state class on any nav link here** — `header.html` is one static file reused verbatim on every page, so a hardcoded `--active` (or equivalent) class would be wrong on every page except one. Active state is set at runtime by `scripts.js` (see the "Active nav state" base helper below) — the markup here should list every link with only its base class.

**Menu toggle visibility:**

The mobile hamburger button must be hidden at desktop and shown at mobile via CSS:

```css
/* desktop default */
.site-header__menu-toggle { display: none; }

/* mobile override */
@media (max-width: 768px) {
  .site-header__menu-toggle { display: flex; }
}
```

Without the desktop `display: none`, the toggle renders on all screen sizes.

---

## footer.html

`footer.html` closes the HTML document. It must end with `</body></html>` and load `scripts.js` before closing:

```html
</main><!-- closes <main> opened in header.html — required for SEO and accessibility -->
<footer class="site-footer">
  <div class="container">
    <p class="site-footer__copy">&copy; <span id="footer-year"></span> [Site Name]. All rights reserved.</p>
    <p class="site-footer__credit">Built with <a href="http://b2.bofrese.dk" rel="nofollow">b2</a></p>
  </div>
</footer>
<script src="/scripts.js"></script>
</body>
</html>
```

**`<main>` landmark:** `footer.html` must close a `<main>` element that was opened in `header.html` — after the `<header>`. This is required for SEO (Google uses `<main>` to identify primary page content) and for accessibility. Add `<main>` to `header.html` immediately after the closing `</header>` tag.

Keep footer content minimal. Adapt based on brand — e.g., add social links, nav columns, or tagline if that aligns with the brand voice. The `scripts.js` path must be absolute (`/scripts.js`), not relative. Style `.site-footer__credit` as muted text (smaller size, reduced opacity or muted colour from the theme's Text Muted token).

---

## scripts.js

Carry the **chosen mockup's full JavaScript** — every bespoke animation, interaction, scroll effect, and
3D/canvas init — and add the three base helpers below. Do **not** reduce the theme to boilerplate: the
craft in the mockup's JS is part of the design and must survive into the live site.

- Keep external libraries (GSAP, Three.js, Motion, …) as `<script src="…">` in `header.html`/`footer.html`;
  `scripts.js` holds the code that drives them.
- If a self-hosted library is used, vendor it as its own `*.js` in the theme folder (the build copies it)
  and load it from `header.html`/`footer.html` before `scripts.js`.
- Gate motion behind `prefers-reduced-motion`; lazy-init heavy 3D.

Always include these base helpers (in addition to the mockup's JS):
1. Mobile menu toggle
2. Smooth scroll for anchor links
3. Footer year auto-update
4. Active nav state

```javascript
// Mobile navigation toggle
const toggle = document.querySelector('.site-nav__toggle');
const nav = document.querySelector('.site-nav');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('site-nav--open');
    toggle.setAttribute('aria-expanded', isOpen);
  });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Footer year
const yearEl = document.getElementById('footer-year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Active nav state — header.html/footer.html are static files concatenated onto
// every page (no per-page templating), so the active link must be set at runtime.
// Adapt the selectors/class name to whatever this theme's nav-link component is.
function markActiveNav() {
  const path = location.pathname.replace(/index\.html$/, '') || '/';
  document.querySelectorAll('.site-nav__link, .mobile-menu a').forEach(link => {
    if (link.classList.contains('site-nav__link--cta')) return; // never mark the CTA active
    let href = link.getAttribute('href');
    if (!href || href.charAt(0) === '#') return;
    href = href.replace(/index\.html$/, '') || '/';
    link.classList.toggle('site-nav__link--active', href === path);
  });
}
markActiveNav();
```

---

## design.md

A human-readable design guide for experienced web designers building new pages within this theme. This file captures the *why and how* behind design decisions — not just palette and fonts, but the rules a designer needs to make autonomous decisions without breaking the visual system.

Generate as `website/theme/{THEME}/design.md`:

```markdown
# [Theme Name] — Design Guide

## Visual Identity
[One sentence that captures the essence of this theme's visual personality.]

## Design Principles

1. **[Principle]** — [2–3 sentences on what this means in practice and how it should drive decisions.]
2. **[Principle]** — [...]
3. **[Principle]** — [...]

## Colour System

| Token | Hex | Role | When to use |
|-------|-----|------|-------------|
| Primary | `#hex` | ... | CTAs, links, key UI elements |
| Secondary | `#hex` | ... | Supporting elements, borders |
| Accent | `#hex` | ... | Highlights, badges, emphasis |
| Background | `#hex` | ... | Page background |
| Surface | `#hex` | ... | Card and section alternate backgrounds |
| Text | `#hex` | ... | Body copy, headings |
| Text Muted | `#hex` | ... | Captions, metadata, secondary copy |

**Colour rules:**
- [e.g., "Accent is used at most once per section — it loses meaning when overused"]
- [e.g., "Never place primary text on a primary background"]
- [e.g., "Surface sections alternate with Background sections — never two consecutive surfaces"]

## Typography System

| Role | Font | Weight | Desktop size | Mobile size | Line height |
|------|------|--------|-------------|------------|-------------|
| Display / H1 | ... | ... | ... | ... | ... |
| H2 | ... | ... | ... | ... | ... |
| H3 | ... | ... | ... | ... | ... |
| Body | ... | ... | ... | ... | ... |
| Caption / Meta | ... | ... | ... | ... | ... |
| Button / Label | ... | ... | ... | ... | ... |

**Typography rules:**
- [e.g., "H1 appears only once per page — above the fold"]
- [e.g., "Body text max-width is 72ch to preserve readability"]
- [e.g., "Never use H1 weight for decorative text — it signals importance"]

## Spacing & Rhythm

Base unit: [e.g., 8px]

| Scale | Value | Typical use |
|-------|-------|-------------|
| xs | ... | Icon gaps, inline spacing |
| sm | ... | Button padding, tag gaps |
| md | ... | Card internal padding |
| lg | ... | Component vertical separation |
| xl | ... | Section vertical padding |
| 2xl | ... | Hero vertical padding, major breaks |

**Spacing rules:**
- [e.g., "Section top and bottom padding is always xl — never lg"]
- [e.g., "Do not use margin between adjacent sections — use padding inside each section"]

## Layout & Grid

- **Max content width:** [e.g., 1200px]
- **Column grid:** [e.g., 12-column, 24px gutters on desktop]
- **Hero:** [e.g., Full-bleed background, min-height 80vh desktop / 50vh mobile]
- **Content sections:** [e.g., Centered single column, max 760px, for long-form prose]
- **Index grids:** [e.g., 3-col desktop / 2-col tablet / 1-col mobile]
- **Breakpoints:** [e.g., Mobile < 640px / Tablet 640–1024px / Desktop > 1024px]

## Component Patterns

Rules for constructing new components that feel native to this theme.

### New section
[Anatomy — e.g., ".section wrapper with xl vertical padding. Optional .section__header (label + title). .section__body for content grid."]

### New card type
[e.g., "Cards use .card base with Surface background, md padding, and a subtle border. Hover state: border-color shifts to Primary. No drop shadows."]

### New CTA block
[e.g., "CTAs are always centered, use a single .btn--primary, with a short supporting line above in Text Muted."]

## Image & Media Treatment

Describe the visual treatment of images. Then add the **Image Size Specifications** table — this is required, not optional. It is read by `/b2:website-review` and `/b2:seo` to resize images to exactly what the design needs.

Derive the `max-width` values from the actual mockup CSS and grid layout — not from generic defaults. A content column that maxes out at 760px needs `max-width: 800` (with 2× headroom for retina), not 1920.

```markdown
## Image & Media Treatment

[Visual treatment description — overlay, aspect ratio, object-fit, placeholder treatment]

### Image Size Specifications

These are the exact pixel sizes this theme renders each image role at.
Used by /b2:seo and /b2:website-review to resize source images correctly.

| Role | CSS component | Max display width | Source max-width | Aspect ratio | Notes |
|------|--------------|-------------------|-----------------|--------------|-------|
| hero | `.hero` | 1920px (full-bleed) | 1920 | 12:5 | loading=eager fetchpriority=high |
| page-hero | `.page-hero` | 1200px | 1200 | 2:1 | background image if any |
| content | `.content-block__image` | 760px | 800 | 4:3 | 800 = 760px + retina headroom |
| card | `.post-list-item__thumb` | 400px | 800 | 3:2 | 800 = 400px × 2 for retina |
| avatar | `.author-avatar` | 80px | 160 | 1:1 | 160 = 80px × 2 for retina |
| logo | `.site-header__logo` | 160px | 320 | — | SVG preferred; PNG fallback |
| og-image | — | — | 1200×630 | 1.91:1 | Social sharing — not in layout |
```

Fill in actual values from this design's mockup and CSS. Remove rows for image roles that don't exist in this design. Add rows for any image roles not listed above.

**Rules for Source max-width column:**
- Full-bleed images (hero, page-hero background): use the actual container max-width in px
- Content images: use the rendered column width + small retina headroom (typically ×1.05)
- Small repeated images (cards, avatars, icons): use rendered size × 2 for retina screens

**SEO and performance requirements — apply to every `<img>` in partials:**
- `alt="[descriptive text]"` — required on every image.
- `width` and `height` — required. Use actual pixel dimensions of the source file (post-resize).
- `loading="lazy"` — on all below-the-fold images.
- `loading="eager" fetchpriority="high"` — on the first/hero image only.
- Use `<picture>` with `<source type="image/webp">` when a `.webp` sibling exists.
- Run `/b2:seo images` to resize, compress, and convert all images using these specs.

## Interactive States

- **Links:** [default / hover / active / focus colors and underline treatment]
- **Buttons:** [hover — e.g., darken 10%; active — e.g., darken 20%; disabled — e.g., 40% opacity, no pointer]
- **Cards:** [hover treatment — e.g., border shifts to Primary, no movement/lift]
- **Nav items:** [active state — e.g., Primary underline 2px, font-weight 600]

## Decorative Elements

Rules for non-structural visual elements specific to this theme:
- [e.g., "Dividers between sections use whitespace alone — never a horizontal rule"]
- [e.g., "Badge/tag elements use accent background at 15% opacity with accent text"]
- [e.g., "Pull quotes use a 4px left border in Primary, italic body font, 1.2× larger"]

## Anti-Patterns

What NOT to do — common choices that break this theme's visual consistency:
- [e.g., "Do not use drop shadows — elevation is expressed through border and colour, not shadow"]
- [e.g., "Do not place more than one accent-coloured element above the fold"]
- [e.g., "Do not mix the display and body typefaces at the same heading level"]
- [e.g., "Do not centre-align body copy — only headings and CTAs are centred"]

## Page Composition

How new pages should be structured:
- **Entry point pages** (homepage, how-it-works): Full `.hero` with mascot panel above the fold. Dense visual. Then content sections. One primary CTA.
- **Destination pages** (docs, about, contact): `.page-hero` at top (compact dark header — eyebrow + h1 + subtitle, no mascot). Then `.content-block` / `.content-block--alt` alternating. Optional `.btn--primary` CTA at end.
- **Above the fold for entry points:** Site header + hero with H1 and primary CTA.
- **Above the fold for destination pages:** Site header + page-hero with page name + punchy h1.
- **CTA frequency:** One primary CTA per page. Secondary CTAs in body sections.
- **Empty states:** [e.g., "Index pages with no items show a centered message in Text Muted with a .btn--secondary to the relevant action"]
```

---

## website/docs/decisions.md — Design Language Section

Append this section to the existing `website/docs/decisions.md` file (do not overwrite the Brand Voice section):

```markdown
## Design Language

**Style:** [1-2 sentence summary of the visual direction]

**Colour palette:**
- Primary: `#hex` — [role, e.g., "CTAs and links"]
- Secondary: `#hex` — [role]
- Accent: `#hex` — [role]
- Background: `#hex` — [role]
- Text: `#hex` — [role]

**Typography:**
- Headlines: [font name, weight] — [where used]
- Body: [font name, weight] — [where used]

**Layout:** [1 sentence: e.g., "Generous whitespace, single-column reading, wide hero sections"]

**Design principles:**
- [principle 1]
- [principle 2]
- [principle 3]
```

This section is used by `/b2:sync` and `/b2:write` to maintain design consistency when generating content.
