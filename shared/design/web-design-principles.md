# Web Design Principles

Shared reference for design-expert and website-review-expert. Apply these principles when creating, iterating, and evaluating pages. These are not rules to check off - they are lenses for making better decisions.

---

## Visual Hierarchy

The single most important principle. Every page must communicate a clear reading order: what to see first, second, third.

**Creating hierarchy:**
- Size and weight dominate - the largest, heaviest element always reads first
- Contrast amplifies - high-contrast elements pull attention; low-contrast elements recede
- Position matters - top-left in Western reading order, followed by centre
- Isolation creates importance - a single element with space around it outranks clustered elements

**Common failures:**
- Multiple elements competing for first position (two large headlines, two bold CTAs)
- Uniform spacing that flattens hierarchy - everything equal means nothing stands out
- Low contrast between sections - pages that feel like one long grey blob
- Using font weight as decoration rather than hierarchy signal

**Evaluation:** Cover the page with your hand and reveal it top-to-bottom. Does the reading order match the content's importance order?

---

## Typography

Typography is the biggest differentiator between generic and premium design.

**Scale:** Establish a modular scale (e.g., 1.25× or 1.333×). Every heading size should derive from it - never arbitrary pixels.

**Contrast:** The headline and body fonts must contrast along at least one axis: weight (light body / heavy headline), classification (serif / sans-serif), or width (condensed / regular). Similarity creates monotony.

**Readability:**
- Body copy: 16–18px minimum, line-height 1.5–1.7, max-width 65–75ch
- Never justify body text - rivers destroy readability
- Adequate leading between paragraphs (at least 1× line-height gap)

**Hierarchy in practice:**
- H1: once per page, above the fold, sets the scale for everything below
- H2: section breaks, visually distinct from H3
- H3: sub-items within a section - not decorative labels
- Never skip heading levels for visual effect

**Openings:** The first line of any section is the most read line. It must reward the reader - specific, interesting, or surprising. Not "Welcome to..." or "We are proud to..."

---

## Colour

Restraint is the mark of a confident designer. More than 5 colours signals confusion, not richness.

**60-30-10 rule:** Background colour 60%, secondary/neutral 30%, accent 10%. Accent colours lose meaning when overused.

**Contrast ratios (WCAG AA minimum):**
- Normal text (< 18px): 4.5:1 against background
- Large text (≥ 18px bold or ≥ 24px regular): 3:1 against background
- UI components (buttons, inputs, focus rings): 3:1 against adjacent colour

**Colour meaning:** Assign each colour a role and protect it. If primary = action, never use primary for decoration. If accent = emphasis, using it on 30% of elements makes it meaningless.

**Neutral is a colour:** A sophisticated palette often has 2-3 neutral tones that do the structural work, freeing the accent to land with impact.

---

## Whitespace and Rhythm

Whitespace is what separates premium from generic. Amateurs fill space; professionals leave it.

**Breathing room:** Sections need generous padding - typically 80–120px vertical on desktop, 48–64px on mobile. Less feels cramped; more feels disconnected.

**Consistent rhythm:** Establish a spacing unit (8px is common) and use multiples: 8, 16, 24, 32, 48, 64, 96. Arbitrary values (13px, 37px) create visual noise the viewer feels but can't name.

**The gap test:** Remove all backgrounds and borders. Does the layout still make sense? If spacing alone communicates grouping and separation, the spacing is right.

**Section alternation:** Alternating background tones (white / light grey, or light / dark) creates rhythm without visual noise. Never more than two adjacent sections with the same background.

---

## Layout and Grid

**The fold is a myth - but the entry is real.** Users scroll, but they must be captured above the fold. The question is not "can they see everything?" - it is "do they *want* to keep scrolling?"

**Hero patterns:**
- Full-bleed: message + CTA above the fold, image as background or full-width panel. For brand-led or emotional entries.
- Split hero: text left, image right (or stacked on mobile). More editorial, shows confidence.
- Centred minimal: headline + subhead + CTA, generous vertical space. Works for focused products.

**Content sections:**
- Prose sections: single column, 65–75ch max-width, left-aligned
- Feature grids: 2-3 columns desktop, 1 column mobile - never more than 3 items per row
- Card grids: consistent aspect ratios, no orphaned single cards on last row (use CSS grid `auto-fill`)

**The Z and F patterns:** Scanners follow a Z (entry pages) or F (content pages) pattern. Place key messages at the start of each horizontal scan line.

---

## Gestalt Principles in Practice

**Proximity:** Elements close together are read as a group. Card title + meta + excerpt must be grouped tightly. The gap between cards must exceed the gap within them.

**Similarity:** Elements that look the same imply equal importance. If two things look the same but aren't equally important, one must be differentiated.

**Continuation:** The eye follows lines and curves. Align elements along invisible grid lines - misalignment breaks the flow and feels amateur.

**Figure/ground:** The page background is ground; content is figure. When ground intrudes into content (e.g., background bleeds into text columns), hierarchy collapses.

---

## Interaction and States

Every interactive element needs all four states: default, hover, active/pressed, focus.

**Focus is non-negotiable:** Keyboard users must always know where they are. Use a visible focus ring - `outline: 2px solid {primary}; outline-offset: 2px` or equivalent. Never `outline: none` without a replacement.

**Hover feedback:** Subtle is enough. Colour shift (10–15% darker), underline, or border-colour change. Avoid movement (translateY, scale) for navigation - it is distracting at high frequency.

**Disabled states:** 40–50% opacity. No pointer cursor. No hover state. Mark with `aria-disabled` not just visual styling.

**Transition timing:** 150–200ms for micro-interactions (hover, toggle). 250–350ms for reveals (modals, dropdowns). Above 400ms feels sluggish. `ease-out` for elements entering; `ease-in` for elements leaving.

---

## Accessibility Baseline

Accessibility is not a feature - it is a quality indicator. A design that fails accessibility fails craft.

- **Colour alone must not convey meaning.** Error states, status indicators, and links must have a secondary signal (icon, underline, pattern).
- **Touch targets:** Minimum 44×44px on mobile. Group small controls (icon buttons, checkboxes) with enough padding.
- **Link text:** Never "click here" or "read more" alone. The link text must make sense out of context (screen readers read links as a list).
- **Images:** Every `<img>` needs `alt`. Decorative images get `alt=""`. Complex images get a caption or description.
- **Semantic HTML:** Use `<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>` - not `<div>` for everything. Screen readers navigate by landmark.

---

## b2 Theme Maintainability

These principles apply specifically to b2 themes. Both design and review decisions must respect them.

**BEM naming is a contract, not a convention.** The sync-expert reads `components.md` to generate partial HTML. If a class is in the HTML but not in `components.md`, sync invents a substitute. If a class is in `components.md` but not in `styles.css`, the page renders unstyled. Every class in every HTML file must appear in both `components.md` and `styles.css`.

**Extend by addition, not modification.** Adding a new modifier class (`.card--featured`) is safe. Renaming or removing an existing class (`.card` → `.item-card`) breaks every partial that uses it. When evolving a theme, only add - never rename or remove.

**Theme files own structure; partials own content.** `header.html`, `footer.html`, and `styles.css` define the container. Partials (`website/partials/*.html`) define the page content. Partials must use only the class vocabulary in `components.md` - never invent new classes in a partial.

**The mockup is the source of truth.** `website/theme/{THEME}/mockup.html` is the canonical visual reference. When reviewing a page, compare its section structure and class vocabulary against the mockup - not against personal preference or generic standards.

**One theme variable, one config.** `website/b2.cfg` holds `THEME=`. Changing the theme name changes all file paths. Never hard-code a theme name in a partial or reference a file by theme name directly - always derive from `b2.cfg`.

---

## What Separates Premium from Generic

These are the most common differentiators when comparing professional-grade sites against template-driven ones:

- **Intentional type scale** - not just big/small but a mathematical relationship between sizes
- **Controlled accent use** - one accent colour used sparingly and purposefully, not scattered
- **Generous and consistent whitespace** - sections breathe; nothing crowds the edge
- **Real content, not placeholder language** - the design is built around actual words, not lorem ipsum
- **Considered empty states** - loading states, zero-item lists, and error states are designed, not afterthoughts
- **Native-feeling interactions** - transitions are fast, feedback is immediate, focus is visible
- **Typography that survives print** - if the page looks good printed in black and white, the hierarchy is real
- **Restraint** - every element has a reason to exist; decoration that adds no meaning is removed
