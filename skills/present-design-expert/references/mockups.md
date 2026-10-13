# Phase 2 - Mockup Concepts

Each concept is a single static HTML file showing a **fixed 6-slide sample set** stacked as
full-viewport sections (scroll to review) - a look-and-feel mockup, not the real reveal.js paginated
runtime. The real per-slide bespoke build happens later, per deck, in `present-build-expert`; this
mockup exists purely to compare directions side by side.

**The fixed sample set (always these 6, in this order - do not add or invent others):**
1. Title/opening slide
2. Section/agenda slide
3. Content + bullets slide
4. Data/chart slide
5. Image-forward slide
6. Closing/CTA slide

Before launching agents, read `website/theme/{THEME}/design.md` and `website/docs/decisions.md` in
full (guaranteed to exist - the Prerequisite Check verified them), and
`${CLAUDE_PLUGIN_ROOT}/shared/design/presentation-design.md`'s Pacing & Beat Philosophy section.
Read `website/docs/status.md` to retrieve the confirmed directions and interview answers (stage
context, motion intensity, audience) from Phase 1. Paste all of this into each agent prompt
verbatim.

**Real-content check (optional).** Look for the most recently modified `docs/presentations/*/*.md`
(by file mtime). If one exists, read it and pass a short excerpt (a handful of representative
slides - title, one content slide, one data slide if present) into each agent prompt under a
`REAL DECK CONTENT (inspiration only)` block, with the instruction: adapt this real content's tone
and subject matter into the fixed 6-slide sample below - do not paste it verbatim, and still cover
all 6 required slide types even if the real deck doesn't have all of them. If no presentation `.md`
exists yet anywhere in the project, omit this block entirely and fall back to inventing sample
content as before.

Ensure the output directory exists:

```bash
root="$(pwd)" && mkdir -p "$root/website/presentation-mockups"
```

**Optional knowledge slice.** If a confirmed direction's motion intensity is "moderate" or
"dynamic", read the relevant file(s) from `${CLAUDE_PLUGIN_ROOT}/shared/design/`
(`animation-motion.md`, `3d-visual-effects.md`) and paste the pertinent lines into that agent's
prompt under a `DESIGN KNOWLEDGE` block. Skip for "minimal" intensity directions.

Launch one agent per direction **simultaneously** using the Agent tool with `run_in_background:
true`. Each writes one concept file in complete isolation - they must not share context or see
each other's output.

**Construct each agent prompt with these blocks in order:**

```
You are an award-winning presentation designer generating a standalone HTML mockup that previews a
presentation theme direction across a fixed set of 6 representative slides.

Write a single self-contained HTML file to: [CONCEPT PATH]

Design direction for this concept: [DIRECTION NAME + INTERPRETATION + VISUAL KEYWORDS + MOTION APPROACH]

Stage context: [from interview - conference stage / client room / webinar / mixed]
Motion intensity: [minimal / moderate / dynamic - from interview]
Audience: [from interview]

---
WEBSITE DESIGN LANGUAGE (source of truth - this presentation theme must read as an extension of it, not a departure):

[PASTE FULL CONTENT OF website/theme/{THEME}/design.md]

---
BRAND VOICE:

[PASTE FULL CONTENT OF website/docs/decisions.md]

---
DESIGN KNOWLEDGE (only if motion intensity is moderate/dynamic):

[PASTE relevant animation-motion.md / 3d-visual-effects.md excerpts, or omit this block entirely for minimal intensity]

---
PACING PHILOSOPHY (always include):

[PASTE the Pacing & Beat Philosophy section from shared/design/presentation-design.md]

---
REAL DECK CONTENT (inspiration only - only if a real presentation .md exists):

[PASTE a short excerpt of the most recently modified docs/presentations/*/*.md - a handful of
representative slides. Adapt this content's tone and subject matter into the fixed 6-slide sample
below; do not paste verbatim, and still cover all 6 required slide types. Omit this block entirely
if no presentation .md exists yet.]

---
MOCKUP REQUIREMENTS:

1. Render exactly these 6 slides, in order, each as a full-viewport (100vh) section, stacked
   vertically so reviewing means scrolling top to bottom:
   a. Title/opening slide - the deck title + a hook subtitle
   b. Section/agenda slide - a 3-4 item agenda or section marker
   c. Content + bullets slide - one idea, max 3 bullets (mirrors the b2 slide-writing rules: no
      sub-bullets, bold the key phrase)
   d. Data/chart slide - a simple representative chart or stat treatment (CSS/SVG or a lightweight
      charting approach - invent plausible sample data, label it clearly as illustrative)
   e. Image-forward slide - full-bleed or large image area with minimal text overlay (use a Lucide
      placeholder or CSS-drawn illustration if no real asset is available)
   f. Closing/CTA slide - echoes the opening, ends on a clear call to action
2. Apply the stage-context adaptation from web-design-principles.md: larger type than a website
   would use (readable from distance), higher contrast, less text per slide, generous whitespace.
3. Deliver the motion intensity level concretely - minimal: near-static, motion only on
   slide-to-slide scroll if at all; moderate: purposeful reveal/transition animations on scroll
   into each section; dynamic: confident animation/3D as this direction's signature (WebGL/Three.js
   via CDN, GSAP, etc. - full creative freedom, no dependency whitelist, same as website mockups).
   Gate all motion behind `prefers-reduced-motion`.
4. FULL CREATIVE FREEDOM on libraries/fonts/CDN assets - same policy as website mockups: any CSS
   technique, any web font, any JS/animation/3D library from a reputable CDN. Put your own CSS in a
   <style> block and JS in a <script> block; external libraries link via CDN in <head>.
5. This concept must look VISUALLY DISTINCT from sibling directions - different layout logic,
   different typographic hierarchy - while clearly sharing the same brand DNA as the website design
   language above.
6. Immediately after the opening <body> tag, include a design-notes comment block the gallery will
   extract, in exactly this form:
     <!-- Design notes: 1-2 sentences on this direction's key design decisions -->

Write only the HTML file. Do not summarise or explain.
```

**Concept paths:**
- Concept 1: `website/presentation-mockups/concept-1.html`
- Concept 2: `website/presentation-mockups/concept-2.html`
- (Concept 3, if a third direction was confirmed: `website/presentation-mockups/concept-3.html`)

**Wait for all agents to complete** before replying to the user.

### Generate the gallery

Build `website/presentation-mockups/index.html` from
`${CLAUDE_PLUGIN_ROOT}/shared/design/gallery-template.html` - the same template `design-expert`
uses, in a separate gallery instance for presentation concepts:

1. Read the template.
2. Replace `{{GALLERY_TITLE}}` (e.g. "Presentation Theme") and `{{COUNT}}` (number of concepts).
3. Replace the `<!-- CARDS -->` marker with one `.card` block per concept, in creation order. For
   each card: `iframe src`/`href` point to that `concept-N.html`; `<h2>` = the direction name;
   `.direction` = "Concept N"; `.notes` = the concept's `<!-- Design notes: … -->` text (fall back
   to the direction name if missing, so no card renders blank).
4. Write `website/presentation-mockups/index.html`.

Then offer to serve and tell the user:
```
{N} concepts ready. Review them side by side in the gallery:

  website/presentation-mockups/index.html

View via the local server: run /b2:serve (or your own static server on website/) and open
/presentation-mockups/index.html.

Which concept do you want to develop further?
```

Use the actual direction names. Do NOT use `open` with a file path.

Update `website/docs/status.md`:
```
  phase: iteration
```

**Wait for the user to name a concept before proceeding.** Do not advance automatically.

Then load `references/theme-lock.md` and continue with the iteration/lock phase.
