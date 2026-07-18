# Sync Expert — Conversion Guide

Detailed HTML generation rules for item conversion and index generation.

---

## Using Mockup HTML as a Layout Reference

`website/theme/{THEME}/mockup.html` is the approved design concept — the user's chosen visual direction. Use it as a compositional guide when generating partials.

**What `components.md` tells you:** which CSS classes exist and what they're for.

**What the mockup HTML tells you:** how those classes compose into actual sections — which elements nest inside which, how sections relate to each other, what the overall page rhythm looks like.

**When generating a partial:**
1. Look at `components.md` for the available class vocabulary
2. Look at the mockup HTML for how those classes are combined in practice
3. Match the compositional patterns from the mockup when structuring sections

**Example:** If `components.md` lists `.content-block` and `.content-block--alt`, the mockup shows whether they alternate (dark/light/dark/light), how much content each contains, and what modifiers are used where. That's the context `components.md` alone doesn't give you.

**If the mockup is large:** The sync-expert SKILL.md instructs extracting only section-level structure. Use that extracted structure — outer nesting + class names per section — as your composition reference.

**If no mockup exists** (design not yet done): rely on `components.md` and content-types.md layout specs only.

---

## HTML Generation Rules

### Semantic Classes Only

Every class used for **standard content** must be listed in `website/theme/{THEME}/components.md`. Do not invent class names for ordinary sections — use the closest matching existing class. The exception is a genuinely new bespoke component (see "Bespoke / high-craft pages"): register it in `components.md` + `styles.css` rather than forcing it into an ill-fitting existing class.

Check `components.md` before generating HTML. Group your class usage by context (shared, per-type, index) to match the components.md structure.

### Choose the Right Form, Not the Nearest One

Before reaching for a code block (`<pre>`/`.terminal`): is this content something the user would literally type or read as terminal output? If not — a file listing, a data flow, a comparison, a sequence of named stages — it deserves a purpose-built component, not code-block styling borrowed because it was already in the vocabulary. Check `components.md` for an existing fit first; if none exists, this is a genuine "Extending the Theme" case (below), not a reason to fall back to `<pre>`. An experienced designer picks the form that matches the content's actual shape — a file tree looks like a file tree, not like a terminal transcript.

### No Visual Styles

Generated HTML is a layout file only. It describes structure, not appearance.

- ✓ `<section class="hero"><h1 class="hero__title">...</h1></section>`
- ✗ `<section style="background: #000; padding: 80px">...`

All visual styling lives in `website/theme/{THEME}/styles.css`.

### No Document Shell

Generated HTML is a fragment — it will be wrapped by the Makefile with header.html and footer.html.

- ✗ `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`, `<header>`, `<footer>`
- ✓ Content sections only, starting with the first meaningful content element

### Bespoke / high-craft pages

The two rules above (semantic classes, no visual styles) are the **default** and the backbone of theme-swappability — follow them for standard content. But b2 pages are allowed to be hand-crafted and visually rich (see the product vision, "hand-crafted pages, surgically maintained"). When a page needs a bespoke interactive element the base vocabulary can't express — an animated hero, a scroll-told section, a Three.js/canvas mount, a WebGL background — support it as follows, in order of preference:

1. **Register it as a component (preferred).** Add the new semantic classes to `components.md`, its CSS to `styles.css`, and any driving JS to the theme's `scripts.js` (or a vendored library loaded from `header.html`). The partial then carries the structure + a mount element (e.g. `<div class="webgl-hero" id="hero-canvas">`). This keeps separation and theme-swappability, and lets other pages reuse the effect. This is the extend-the-theme path (below).
2. **One-off escape hatch.** For a genuinely unique, non-reusable effect, the partial may carry its own scoped `<style>` / `<script>` block and hook IDs. This trades theme-swappability for that one page — use it deliberately, not by default.

Either way, the libraries and fonts the effect needs live in the theme (`header.html` CDN/vendored, `scripts.js`), so they load site-wide. Never strip a page's bespoke markup, hook IDs, or scoped effect blocks during a re-sync — they are intentional craft (see "Handling Existing Partials").

---

## Item Conversion — Structure

Map markdown content to semantic HTML sections using the type's "Default layout" from `content-types.md`.

**Example: post type**
- Default layout: `post-header → body-text → tag-list`

```html
<article class="post">
  <header class="post-header">
    <h1 class="post-header__title">[title value from frontmatter]</h1>
    <p class="post-header__meta">
      <time class="post-header__date" datetime="[date value]">{{ date formatted }}</time>
    </p>
    <p class="post-header__summary">{{ summary }}</p>
  </header>

  <div class="post-body">
    <!-- Converted markdown body content here -->
    {{ body as HTML paragraphs, headings, lists, blockquotes }}
  </div>

  <!-- If tags frontmatter field is present and non-empty, render one <span class="tag"> per tag -->
  <footer class="tag-list">
    <span class="tag">example-tag</span>
    <!-- repeat for each tag value -->
  </footer>
</article>
```

**Markdown body conversion:**
- `# Heading` → `<h2>` (h1 is reserved for the post title)
- `## Heading` → `<h3>`
- `**bold**` → `<strong>`
- `*italic*` → `<em>`
- Paragraphs → `<p>`
- `- list item` → `<ul><li>`
- `1. list item` → `<ol><li>`
- `> blockquote` → `<blockquote>`
- `` `code` `` → `<code>`
- ` ```code block``` ` → `<pre><code>`
- `[text](url)` → `<a href="url">text</a>`

**Example: page type (root-level)**

Pages come in two sub-types. Read `content-types.md` to confirm which applies. The file names the entry point pages explicitly.

**Entry point pages** (e.g., index.md, how-it-works.md): Start with `.hero` + `.hero__mascot-panel`. Then content sections. Never entry-point a destination page.

**Destination pages** (e.g., about.md, docs.md, showcase.md): Start with `.page-hero` — NOT `.hero`, NOT raw content. Then `.content-block` / `.content-block--alt` alternating sections.

The `page-hero` eyebrow is the page name ("Documentation", "About"). The `page-hero__title` is a short punchy claim with one `<em>` for blue emphasis. The subtitle is one sentence.

```html
<!-- Entry point page -->
<section class="hero" aria-labelledby="page-title">
  <div class="hero__content">
    <div class="hero__eyebrow">Eyebrow text</div>
    <h1 class="hero__title" id="page-title">
      <span class="hero__title-line">Line one</span>
      <span class="hero__title-line hero__title-line--blue">Line two</span>
    </h1>
    <p class="hero__body">Subtitle text.</p>
    <div class="hero__actions">
      <a href="#install" class="hero__cta-primary">Primary CTA</a>
    </div>
  </div>
  <div class="hero__mascot-panel">
    <!-- mascot SVG goes here -->
  </div>
</section>

<section class="content-block">
  <h2 class="content-block__heading">Section heading</h2>
  <div class="content-block__body">
    {{ body content }}
  </div>
</section>

<!-- Destination page -->
<section class="page-hero" aria-labelledby="page-title">
  <div class="page-hero__inner">
    <span class="page-hero__eyebrow">Page Name</span>
    <h1 class="page-hero__title" id="page-title">Short punchy claim<br><em>with blue emphasis</em></h1>
    <p class="page-hero__subtitle">One sentence subtitle.</p>
  </div>
</section>

<section class="content-block" id="section-anchor">
  <h2 class="content-block__heading">Section heading</h2>
  <div class="content-block__body">
    {{ body content as paragraphs, lists, pre/code blocks }}
  </div>
</section>
```

**Important for destination pages:** Add `id` attributes to sections that are linked from the footer or nav (e.g., `id="quickstart"`, `id="commands"`, `id="faq"`). Check the footer.html and content-types.md for which anchors are expected.

---

## Index Generation — Structure

Index files aggregate frontmatter from all items in the type's folder and present a listing.

Use the type's "Index layout" from `content-types.md`.

**Example: post index**
- Index layout: `post-listing → (post-list-item)* reverse-chronological`

Read all `website/src/posts/*.md` files. Extract frontmatter. Sort by `date` descending.

```html
<section class="post-listing">
  <div class="container">
    <h1 class="post-listing__title">Posts</h1>

    <ul class="post-list">

      <li class="post-list-item">
        <a href="/posts/slug.html" class="post-list-item__link">
          <h2 class="post-list-item__title">[title value from frontmatter]</h2>
          <time class="post-list-item__date" datetime="[date value]">[date formatted, e.g. March 2, 2026]</time>
          <p class="post-list-item__summary">[summary value from frontmatter]</p>
        </a>
      </li>

      <!-- repeat for each post -->

    </ul>
  </div>
</section>
```

**Example: product index**
- Index layout: `product-grid → (product-card)*`

```html
<section class="product-grid">
  <div class="container">
    <h1 class="product-grid__title">Products</h1>
    <ul class="product-list">
      <li class="product-card">
        <a href="/products/slug.html">
          <h2 class="product-card__title">[title value from frontmatter]</h2>
          <p class="product-card__tagline">{{ tagline }}</p>
        </a>
      </li>
    </ul>
  </div>
</section>
```

---

## URL Slug Generation

Derive the URL path for index links from the filename. **Include the `.html` extension** — Apache httpd and `python3 -m http.server` serve flat `.html` files and do not auto-resolve extensionless URLs:

- `website/src/posts/my-first-post.md` → href `/posts/my-first-post.html`
- `website/src/products/blue-widget.md` → href `/products/blue-widget.html`

Exception: the site root (`/`) maps to `index.html` by Apache's DirectoryIndex — use `/` not `/index.html` for home links.

**Link to the most specific anchor available.** When a link references a specific named item on another page — a command, a FAQ entry, a numbered step — rather than the page or section in general, link to that item's own anchor if the target page defines one, not the enclosing section's anchor. If the target item has no anchor yet, that's a signal the target page's convention needs one — flag it rather than settling for the nearest parent anchor.

---

## Handling Missing Frontmatter Fields

If a `.md` file is missing an expected frontmatter field (e.g., no `summary`, no `tags`):

- Omit the corresponding HTML element entirely
- Do not render empty tags (no `<span class="tag"></span>`)
- Do not use placeholder text (no "No summary available")

Example: if `summary` is absent, omit the `<p class="post-list-item__summary">` element from the index listing for that item.

---

## Handling Existing Partials

When a partial already exists (from a previous sync or manual edit):

1. Read the existing HTML
2. Compare its structure against the current `.md` source
3. Update content that has changed (title, body, frontmatter fields)
4. Preserve the HTML structure and semantic class choices
5. Do not reset to a "pristine" AI output

The goal is surgical content updates, not wholesale regeneration. Only regenerate from scratch if the existing HTML is genuinely malformed. Bespoke effect blocks, hook IDs, scoped one-off `<style>`/`<script>`, and registered bespoke classes are intentional craft — preserve them; do not treat them as errors to reset.

**Orphaned sections:** "preserve structure" means preserve structure for content that still exists in the current source — not retain a partial's section indefinitely once its source paragraph/list/reference is gone. Before finishing a re-sync, check each existing top-level section in the partial against the current `.md`: if a section has no plausible corresponding content in the new source at all (not just reworded — genuinely absent), remove it rather than carrying it forward as an orphan. Bespoke partial-only additions (a pull-quote, a compare-figure) are the deliberate exception — those exist to serve source content that *is* still present, not to persist independently of it.

### Redesign — new theme vocabulary

On a redesign a new theme was generated, so `components.md` changed while the content `.md` did not. Re-evaluate every existing partial against the new `components.md`, using its `## Redesign delta` (Reused / New / Dropped-or-renamed) and the new `mockup.html` composition:

- **All the partial's classes still exist (reused):** keep it as-is — apply content updates only if the `.md` also changed. Reused semantic names are exactly what lets pages carry over untouched.
- **Some classes were renamed:** remap old → new class names; preserve structure and content.
- **Classes were dropped, or the design paradigm changed for that section:** redo the affected sections against the new mockup composition and vocabulary. A genuinely different design (new grid, new hero paradigm) may warrant rebuilding the partial's structure, not just renaming — re-evaluate, don't force old structure into the new design.
- Preserve any bespoke/registered per-page components whose classes survive.

Reuse where the vocabulary carried over; redo where it changed. A theme swap stays cheap when names were reused, without blocking a bold redesign that needs new structure.

---

## Extending the Theme

Only extend the theme when no existing class in `components.md` fits the semantic need. Do not extend for visual variation — use existing modifier classes (`--alt`, `--primary`, etc.). Do extend for genuinely new structural patterns (a new content type section, a component that doesn't exist in the theme at all).

**When to extend:**
- Content type has a layout requirement with no matching component (e.g., a gallery grid, a comparison table, a timeline)
- The new component is structurally distinct — not a visual variant of an existing one
- A page needs a bespoke interactive/animated/3D element (animated hero, scroll-told section, canvas/WebGL mount) — register it as a component with its CSS in `styles.css` and driving JS in the theme's `scripts.js` (or a vendored library), so it is preserved and reusable

**When NOT to extend:**
- A different colour or size is needed — use modifier classes or inline style
- The component already exists under a slightly different name — use the existing class and note it

**How to extend (sync-expert Step 5):**
1. Name the new class semantically (`.gallery-grid`, not `.flex-container`)
2. Read `design.md` to understand the colour system, spacing scale, and component patterns
3. Add CSS to `styles.css` under the nearest matching section heading
4. Add the class to `components.md` in the appropriate group
5. If the pattern is reusable, document it in `design.md` under "Component Patterns"
6. Report the extension in the sync summary
