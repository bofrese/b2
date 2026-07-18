---
name: website-review-expert
description: This skill should be used when the user runs "/b2:website-review", asks to "review the website", "check the layout", "screenshot the site", "does this look right", "judge the design quality", "does this live up to the mockup", or wants to visually verify a page against the design. Takes screenshots via Playwright, evaluates against the user's own design system AND against art-director-level visual quality (interest, coherence, boring text pages), and fixes issues — including adding missing reusable theme components when a page has no tool to be visually interesting with.
---

# b2 Website Review Expert

Screenshot dist/ pages and evaluate them both for design-system compliance and for visual quality as an outside art director would judge them. Fix layout issues — in partials, or in the theme itself when the fix is a missing reusable pattern, not a one-off. Flag copy issues without modifying copy.

Act as an award-winning web designer and art director reviewing a junior's build against your own mockup. Compliance with `components.md` is necessary but not sufficient — a page can use every class correctly and still be dull, misaligned in spirit, or visually flat compared to the mockup's ambition. Do not accept "technically matches the system" as good enough if the page is boring.

---

## On Entry

If the user provided a page argument (e.g., `/b2:website-review about.html`), review only that page.

If no argument was given, review all `.html` files in `website/dist/` in alphabetical order.

---

## Step 1 — Load Design Context

Read `website/b2.cfg` if it exists. Look for a `THEME=` line. Default: `THEME=b2`. Theme directory: `website/theme/{THEME}/`.

Read these files using the Read tool before evaluating anything:

1. `website/theme/{THEME}/components.md` using the Read tool (required — halt if missing: "Run `/b2:design` first.")
2. `website/theme/{THEME}/mockup.html` using the Read tool — if it exists, extract section-level structure (outer div/section nesting + class names per section). If large (>150 lines), extract structure only, do not load full content. Skip if missing.
3. `website/docs/decisions.md` using the Read tool — brand voice and design language section. Skip if missing.

These files define THIS project's design system. All evaluation criteria must derive from them. Do not apply generic design opinions.

---

## Step 2 — Verify Server Is Running

Screenshots via `file://` URLs render unstyled because CSS uses absolute paths (`/styles.css`). A local server must be running.

Check if the server is reachable (Bash tool):

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8099/ 2>/dev/null || echo "unreachable"
```

If unreachable, stop:

> "The local server is not running. Start it with `/b2:serve`, then re-run `/b2:website-review`."

If reachable, use `http://localhost:8099/{page}` URLs for all screenshots — not `file://` paths.

---

## Step 3 — Screenshot

Create the screenshot directory if needed (Bash tool):

```bash
mkdir -p .playwright-mcp
```

For each page to review, take a screenshot.

**Playwright detection — try in order:**

1. **MCP browser tools** — If the `browser_navigate` and `browser_take_screenshot` tools are available in this session (Playwright MCP configured as a Claude Code plugin), use them directly:
   - Navigate: use `browser_navigate` with `http://localhost:8099/{page}`
   - Screenshot: use `browser_take_screenshot` with `filename: ".playwright-mcp/{page}.png"`

2. **npx playwright** — If MCP tools are not available, check CLI (Bash tool):
   ```bash
   npx playwright --version 2>/dev/null || echo "not found"
   ```
   If found: `npx playwright screenshot http://localhost:8099/{page} .playwright-mcp/b2-review-{page}.png`

3. **playwright CLI:**
   ```bash
   playwright --version 2>/dev/null || echo "not found"
   ```
   If found: `playwright screenshot http://localhost:8099/{page} .playwright-mcp/b2-review-{page}.png`

4. **None available — halt:**
   > "Playwright not found. Install it with:
   > - `npx playwright install` (requires Node.js)
   > - Or add the Playwright MCP plugin to Claude Code
   >
   > Then re-run `/b2:website-review`."

**Cache staleness (MCP browser tools only):** an MCP browser session persists across this whole review, so a stylesheet fetched once stays cached in that tab even after a rebuild changes it on disk — a real fix can then screenshot as if it never happened. Before any screenshot that follows a rebuild (Step 5's re-screenshot after a fix, or re-running mid-session after theme edits), force revalidation first: `browser_evaluate` a `fetch('/styles.css', {cache:'reload'})` (and `/scripts.js` if it changed), then navigate/re-navigate before capturing. The CLI paths (`npx playwright`/`playwright`) spin a fresh context per invocation and aren't affected.

**Scroll-reveal false positives:** if a themed section uses a scroll-triggered reveal (`.reveal`/`.is-visible` or similar — check `components.md` for the pattern name), a full-page automated screenshot can show it blank or collapsed, because its opacity-0 initial state never gets triggered without real scroll/IntersectionObserver firing. Before flagging such a section as broken, verify by scrolling it into view (`browser_evaluate` an `element.scrollIntoView()`) and re-screenshotting that viewport — don't trust the full-page capture alone for anything using this pattern.

---

## Step 4 — Evaluate

Read `${CLAUDE_PLUGIN_ROOT}/shared/design/web-design-principles.md` using the Read tool. This provides the visual and structural criteria for evaluation — hierarchy, typography, colour, whitespace, rhythm, accessibility, and b2 maintainability principles. Apply these alongside the project-specific design system loaded in Step 1.

Evaluate each screenshot against THIS project's design system (from Step 1). Do not apply generic standards.

**Evaluation criteria — derive from components.md, mockup.html, and web-design-principles.md:**

1. **Class vocabulary compliance** — Are the classes used in the partial all listed in `components.md`? If a class appears in the page HTML that isn't in `components.md`, flag it.

2. **Layout composition** — Does the section structure (order, nesting) match the patterns in the mockup HTML? For example: if the mockup shows hero → content-block → content-block--alt → cta, does this page follow that rhythm for the sections it has?

3. **Visual hierarchy** — Is there a clear reading order? Does the page have one dominant element above the fold? Are competing elements pulling equal attention when one should win?

4. **Typography hierarchy** — Is there one `h1` per page? Are heading levels nested correctly? Does the type scale create genuine contrast between H1 / H2 / H3 / body?

5. **Spacing and rhythm** — Do sections have consistent vertical spacing? Are alternating sections (e.g., `.content-block` vs `.content-block--alt`) used where the mockup uses them? Is whitespace generous enough to let content breathe?

6. **Colour and contrast** — Does text meet WCAG AA contrast ratios against its background? Is the accent colour used sparingly and purposefully, or scattered throughout? For state colours (active nav, hover, links), check `website/docs/decisions.md`'s palette role assignments (e.g. "blue = links/active/structural, orange = CTA/highlight/energy") before proposing a change — a colour that reads "subtle" is often a documented, deliberate choice to keep the other accent's meaning intact (using orange everywhere dilutes it as a CTA signal). If genuinely too subtle, prefer strengthening the existing role (bolder weight, added background/glow) over swapping to the other accent.

7. **Responsive navigation** — Is the mobile menu markup present? Does the menu toggle use the correct state class from `components.md`? Are touch targets adequately sized? **Active-link correctness:** `header.html`/`footer.html` are single static files concatenated onto every page verbatim (see `assemble.sh`/`Makefile` — no per-page templating). Check `scripts.js` (or the header markup) actually sets the current page's nav link to the active-state class at runtime — a hardcoded `--active` on one link in the static HTML will be wrong on every other page. Verify in the browser (evaluate the DOM after load), not just by reading the static partial — the static markup will look "correct" for whichever page it was authored against and wrong everywhere else.

7b. **Rendered-DOM correctness** — Static markup review misses runtime layout bugs. For any component with repeated sibling elements styled by a shared selector (e.g. `.terminal__bar span`), check the *rendered* result, not just the CSS rule: does a broad selector accidentally catch an element it shouldn't (a label/title span picked up by a "make every span a dot" rule)? Screenshot at the component level (not just full-page) when a component looks even slightly off, and compare spacing/alignment of siblings against each other.

8. **Accessibility baseline** — Are focus states visible? Do links have descriptive text? Do images have `alt` attributes? Are semantic landmark elements (`<nav>`, `<main>`, `<header>`, `<footer>`) present?

9. **SEO baseline** — Run a quick audit against the dist/ page being reviewed (Bash tool):

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/seo-audit.sh" "{page}"
   ```

   Flag any `ISSUE:` lines as `[SEO]` issues. Flag `WARN:` lines about title, H1, meta description, and missing alt text. Do not flag schema/OG/sitemap warnings here — those are for `/b2:seo`.

   Specifically check:
   - Is the `<title>` tag unique to this page, or the same generic title on every page? (duplicate = `[SEO]` issue)
   - Is there exactly one `<h1>` that matches the page's primary topic?
   - Do all `<img>` tags have meaningful `alt` text?
   - Are `<img>` tags missing `width`/`height` attributes? (causes layout shift)
   - Is the `<main>` landmark present?

10. **Visual interest (art direction)** — Judge the page the way an outside art director would, independent of class compliance:
    - Does this page look like a deliberate composition, or a template dump of paragraphs? A page can pass every check above and still be flat.
    - For pages that are mostly text (about, docs, long-form posts): is there at least one visual break per ~2-3 screens of scroll — a pull quote, stat highlight, callout, divider, or image? A wall of body text with only h2/h3 breaks is a fail even if every class is correct.
    - Does the page match the *ambition* of `mockup.html`, not just its literal classes? If the mockup uses bold type contrast, generous negative space, or a strong focal element and the page reads as generic by comparison, flag it.
    - Is there visual coherence with other reviewed pages — consistent use of whatever visual-interest devices exist, not a one-off treatment invented per page?

11. **Illustration opportunity** — Where a page would be materially improved by an image and has none (a hero with no visual, a long text section with no breathing room, a concept that's hard to grasp in prose alone), flag it with `[VISUAL]`. Give a ready-to-run invocation, not just a pointer — state the page, the target slot/size (from `design.md`'s Image Size Specifications table, or the component role: hero/content/card), and a one-line concept hint, e.g.: `/b2:illustrate about.html — "Why B2 exists" section, content-block image (~800px), concept: old abandoned site vs. live B2 site, before/after contrast`. Check `docs/product/illustration-style.md` first if it exists — the concept hint must fit the established illustration style, not invent a new one.

12. **Link resolution** — For every `href` starting with `#` or containing `.html#`, confirm the target `id` actually exists on the destination page (same page for `#x`, the linked page for `page.html#x`). A CTA or nav link pointing at a non-existent anchor is a dead link even though it renders as a normal-looking button.

**Copy issues:** If you identify content that seems wrong, missing, or off-brand — flag it in the report with `[COPY]` prefix but do NOT edit the content. Copy is the domain of write-expert.

---

## Step 4b — Bespoke Art Direction Pass

Criteria 1-11 catch compliance and generic flatness. This step goes further: judge whether each page feels *individually hand-crafted for its content*, or whether it reads as the same modular blocks reshuffled — a competent template, not a designed page. A page can pass every criterion above and still feel like a CMS dumped it out.

Run this once per page, after the compliance pass, using the screenshot plus the partial's content:

**Three questions per page:**

1. **What is this page for, and who's reading it at this moment in their journey?** A docs/reference page, a persuasion page, and a proof/showcase page all want different rhythms — reference wants fast scanning, persuasion wants pacing and momentum, proof wants texture and specificity. If every page uses the same section rhythm regardless of purpose, that's the tell.

2. **If a design agency had a full day to lay out only this page's content, what would they NOT reuse from the generic template?** Look for a genuine opportunity, not an invented one: a stat worth calling out at scale, a step sequence that could be a real diagram instead of a stacked list, a comparison that wants a table or side-by-side, a concept that's hard to grasp in prose and wants a diagram.

3. **Where does generic UI chrome break the illusion that this page belongs to its world?** Off-the-shelf-feeling widgets — a plain terminal window, a stock button, a bare table, a default `<blockquote>` — read as "component library default" rather than "designed for this theme." On a themed site (space, editorial, brutalist, whatever `design.md` establishes), these are the first things that feel bought, not made. Example: a code block styled as a generic macOS terminal on a deep-space sci-fi theme reads off-brand — a spaceship console/HUD treatment (amber/blue readouts, subtle scanline or corner-bracket framing) would feel native, *without* over-decorating it into illegibility. Apply the same lens to every generic-feeling element found: buttons, tables, blockquotes, form inputs, list markers, dividers.

**Output — a Design Proposals list, not silent fixes.** For each opportunity found, write one concrete, scoped proposal: what element, what treatment, why it fits this theme specifically (cite `design.md`/`website/docs/decisions.md` language, not generic taste). Distinguish:
- **Reskin** — an existing shared component (e.g. `.terminal`) gets a new visual treatment in place. Affects every page using it — list them. State the exact criterion for which instances qualify, not "everywhere this pattern appears" — a pattern used for both genuine command-entry moments and pure reference/diagram content usually should NOT be extended uniformly to both. Naming the criterion up front means the proposal can be applied precisely instead of needing a second pass to narrow it down.
- **New component** — something the theme has no vocabulary for yet (diagram, comparison table, timeline variant).
- **Illustration** — a concept/section that wants imagery. See criterion 11 for the required `/b2:illustrate` invocation format (page, slot/size, concept hint) — don't just say "consider illustrating this."

**Token consistency across near-duplicate elements.** When a page has several elements that are variations on one idea — multiple code/command blocks, multiple callouts — grep the whole site for that pattern (not just the current page) before proposing a fix. A reskin or new colour convention (e.g. "comments are muted, commands are orange, prompts are blue") must apply to every instance of that pattern site-wide, not just the one under review — a fix that makes one code block look crafted while three others nearby stay plain generic `<pre>` is a net loss for coherence, not a win. Search partials with grep for the shared class/tag before finalizing a proposal's affected-pages list.

Present the Design Proposals list to the user in the Step 6 report and **stop for confirmation before implementing any of them** — these are theme-level, cross-page, or illustration-commissioning decisions, not mechanical fixes. Compliance and SEO fixes from Step 5 still apply automatically; art-direction proposals do not.

---

## Step 5 — Fix Issues

Fix layout and SEO issues directly in the relevant files. Work in this order: template fixes first (they affect all pages), then partial fixes (single page).

**Layout fixes** — edit `website/partials/{page}.html`:
1. Read the partial.
2. Apply the specific fix (add missing class, correct structure, fix heading level, etc.).
3. Describe the change: "Added `.content-block--alt` alternation to sections 3 and 5."

**SEO fixes in partials** — fix directly in `website/partials/{page}.html`:
- Missing `alt` on `<img>` → add descriptive alt text based on the image content/filename.
- Missing `width`/`height` on `<img>` → detect from `website/src/images/` and add. If dimensions can't be detected, flag with `[SEO-MANUAL]`.
- Missing `loading` on `<img>` → add `loading="lazy"` (or `loading="eager" fetchpriority="high"` for the first/hero image).
- Missing `<h1>` → fix heading level in the partial.
- Multiple `<h1>` tags → demote extras to `<h2>`.
- Missing `<main>` landmark → this is a template issue — fix in `website/theme/{THEME}/header.html` (add `<main>` after `</header>`) and `website/theme/{THEME}/footer.html` (add `</main>` before `<footer>`).

**Oversized images** — when an image in the partial appears oversized (large file, or source file dimensions far exceed what the design needs):

1. Read `website/theme/{THEME}/design.md` and look for the `### Image Size Specifications` table.
2. Identify the image's component role by the CSS class of its parent element (e.g., `.hero` → hero role, `.content-block__image` → content role, `.post-list-item__thumb` → card role).
3. Read the **Source max-width** value for that role from the table.
4. Run `prep-images.py` with that exact value (Bash):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/seo-expert/scripts/prep-images.py" website/src/images/{filename} --fix --max-width {source_max_width}
   ```
5. If `design.md` is missing or has no Image Size Specifications table, use 1920px for hero/full-bleed images and 800px for content/card images as safe defaults.
6. After resizing, update `width`/`height` attributes in the partial to match the new dimensions.

**SEO fixes that belong to other skills** — do NOT fix here, flag instead:
- Missing meta description, title tags, canonical, OG, schema → flag with `[SEO]` and suggest `/b2:seo`
- Duplicate titles across pages → flag and suggest `/b2:seo`

**Visual-interest fixes — theme vs. partial:** When a `[VISUAL]` finding needs a pattern that doesn't exist yet in `components.md` (e.g. no pull-quote, callout, or stat-highlight component at all), do not hand-roll a one-off `<style>` block in the partial. Add the reusable component to the theme instead, since the same gap will recur on every text-heavy page:

1. Design the component in the mockup's visual language (type scale, colour, spacing already established in `design.md`/`styles.css`) — not a generic bootstrap-style callout.
2. Add its CSS to `website/theme/{THEME}/styles.css` and document the class in `components.md`.
3. Confirm with the user before committing to the new pattern (this is a shared theme change, not a page-local one): "No pull-quote pattern exists in the theme — I'd add `.pull-quote` to styles.css/components.md and use it here and on {other pages with the same gap}. OK?"
4. Apply the new class in the partial(s) that need it.

If the user declines the theme addition, apply the closest existing pattern instead and flag the gap in the report rather than inventing scoped CSS.

**Implementing an approved Design Proposal from Step 4b** (only after the user confirms which ones to do):

- **Reskin of a shared component** (e.g. `.terminal` → spaceship console): edit the CSS in place in `styles.css` under the existing class — do not fork a new class unless the old visual is still needed elsewhere. Since shared components render on every page that uses them, re-screenshot *all* affected pages after the change, not just the one under review.
- **New component**: same procedure as the pull-quote/callout case above — add to `styles.css` + `components.md`, apply where relevant.
- **Illustration**: do not generate it here. Report the concept and section, and tell the user to run `/b2:illustrate` for it.

After fixing, reassemble the affected pages:

**If make is available:**
```bash
cd website && make
```

**If not:**
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/build-expert/scripts/assemble.sh"
```

Then re-screenshot the fixed page and confirm the issue is resolved.

---

## Step 6 — Report

```
UI Review: about.html

Screenshot: http://localhost:8099/about.html ✓

Fixed (3):
  1. [LAYOUT] .content-block sections 3 and 5 missing --alt modifier
     → added .content-block--alt class ✓
  2. [LAYOUT] h3 headings not using .content-block__subheading class from components.md
     → updated class on 3 headings ✓
  3. [SEO] 2 images missing width/height attributes (CLS risk)
     → added width/height from source files ✓

Flagged — needs action (3):
  4. [COPY] Opening paragraph is generic — does not match brand voice from website/docs/decisions.md
     → Run /b2:write to update website/src/about.md
  5. [SEO] No meta description on this page
     → Run /b2:seo for full SEO fix (titles, descriptions, schema, OG)
  6. [VISUAL] 900 words of unbroken body text, no visual break — flat compared to mockup's ambition
     → No pull-quote/callout pattern exists in theme; propose adding one (see Step 5) or run /b2:illustrate for a section image

Design proposals (2) — confirm before I implement:
  A. [REFIT] .terminal reads as a generic macOS terminal window on a deep-space theme
     → Reskin as a spaceship console: amber/blue readout colours, corner-bracket frame instead of traffic-light dots. Affects: index.html (install section), docs.html (command reference). Implement? (yes/no)
  B. [ILLUSTRATION] "Why B2 exists" section has no visual — hard-to-grasp inertia concept, all prose
     → /b2:illustrate about.html — "Why B2 exists" section, content-block image (~800px), concept: old abandoned site vs. live B2 site, before/after contrast

Result: 3 fixes applied. 3 issues flagged. 2 design proposals awaiting confirmation.
```

If no issues found:

```
UI Review: about.html

Screenshot: http://localhost:8099/about.html ✓

No layout or SEO issues found. Page matches design system.
```

**SEO escalation rule:** If the audit reveals 3 or more `[SEO]` issues across the pages reviewed, add at end of report:
> "Multiple SEO gaps found. Run `/b2:seo` for a full audit and fix — it covers meta descriptions, titles, schema, Open Graph, sitemap, and image optimisation."
