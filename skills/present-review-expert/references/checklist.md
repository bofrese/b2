# Review Checklist - Five Dimensions

Apply all five to every slide under review. Most slides fail on layout/graphics/dynamics well
before text - a slide with perfect copy and a dead-space wall on the right is still a weak slide.

---

## 1. Text

Ask, in order:

- **Does the headline promise what the slide delivers?** A headline naming three things when the
  slide has four (or vice versa) is a real defect, not a nitpick - fix by either extending the
  headline or, often better, shortening it so the body/visual does the enumerating instead. A
  short, non-enumerating headline ages better as the slide's content changes.
- **Is anything redundant with something already said?** Two common patterns: (a) the closing line
  restates the headline's claim in different words ("10x the technical debt" headline + a separate
  "debt compounds at 10x speed" sentence later - cut the second, the headline already said it); (b)
  a caveat or qualifier that doesn't change the argument and mainly hedges - cut it unless the
  presenter specifically wants the hedge on record.
- **Would a visual say this better than a sentence?** If a bullet point is describing a structure
  (a fork/decision, a sequence, a comparison, a proportion), a diagram usually replaces the
  sentence outright rather than sitting beside it - see dimension 4.
- **Is anything here only readable because of what the presenter will say out loud?** If notes
  won't be visible during delivery (see SKILL.md's on-entry question), every claim needed to
  understand the slide must be text or graphic *on* the slide - a slide that only makes sense with
  narration is broken for this presenter, not just thin.
- **Does phrasing sound natural, not translated?** For a non-native English speaker's copy, prefer
  the idiomatic construction and say why in one sentence if asked (e.g. "if that's how X" is the
  standard hypothetical-conditional pattern; "if this is how X" implies pointing at something
  already on screen) - don't just assert taste, give the grammatical reason so the presenter can
  judge it themselves next time.

## 2. Layout

- **Is there a large empty region with no compositional reason?** Dead space is fine when it's
  deliberate breathing room around a genuinely short, punchy statement (see dimension 5's "minimal
  statement" pattern) - it's a defect when it's just what's left over after placing a normal-length
  paragraph in a single narrow column. Distinguish the two by asking whether the slide is trying to
  be quiet on purpose.
- **Does line-wrapping happen at good points?** Check both a normal (900px) and a short (700px)
  viewport height - content that wraps fine at one height can wrap awkwardly, overflow, or get
  clipped at the other. Never trust a single window size as "verified" (this theme is fluid, not
  scaled - see the theme's own design.md Anti-Patterns).
- **Is emphasis (bold, colour, size) marking what's actually important**, or scattered decoratively?
- **Does the slide's density match its neighbours' rhythm?** Three image-heavy slides in a row
  flattens the pacing even if each one is individually fine - a deliberately spare, text-only slide
  between two illustrated ones can be the *right* choice, not a gap to fill. Ask whether a proposed
  fix is solving a real problem or just matching the previous slide's treatment out of habit.
- **Is an unbalanced two-column split fixed with a `flex-grow` ratio, never a fixed px `min-width`?**
  A px floor on the cramped side just moves the dead space to the other column at a different
  viewport width - see `implementation-gotchas.md`. If widening the window doesn't relieve the
  imbalance, the fix was a px value, not a ratio.
- **Does the component's own centering/max-width actually take effect, or is a parent container
  capping it first?** A grid/split with its own `max-width` nested inside a narrower single-column
  wrapper plateaus at the parent's cap regardless of viewport - check the ancestor chain, not just
  the component's own CSS, when a layout looks stuck too narrow.

## 3. Typography consistency

- **Does this slide's body copy use the deck's real size tokens**, or a bespoke clamp/rem value
  invented for this slide alone? A "close enough" one-off is the single most common typography
  defect - it looks fine in isolation and only shows as a problem once several slides doing the
  same job (a lead paragraph under a headline, a secondary caption) are compared side by side and
  turn out to all be subtly different sizes for no reason.
- **Font family**: only the families in the theme's documented Typography System table should
  appear. A stray font-family on one slide is almost always a copy-paste leftover, not a deliberate
  choice.
- **Does the theme's own documented type-scale table match what's actually implemented?**
  Documentation drifts - a table entry can describe a value the component's real CSS no longer
  uses. Spot-check at least one documented role against its actual `theme.css` rule per session.
- Run the full deck-wide version of this check via `references/typography-audit.md` rather than
  relying on catching it slide-by-slide - one-off sizes are easy to miss individually and only
  become obvious in aggregate.

## 4. Graphics / visual interest

- **Is this a text-only slide with no other visual interest?** The theme's shared geometric-shape
  vocabulary (arc, diagonal panel, circle, etc. - check the theme's design.md) exists specifically
  for this case. A minimal, deliberately spare slide (see dimension 5) doesn't need one; a slide
  that's just a paragraph filling a third of the frame does.
- **Does the slide's content describe a structure that wants a diagram instead of prose?** Concrete
  tells: "explore N options, pick one" → a fork/converge diagram, not a sentence. "X% of the time
  goes to Y" → a proportional bar, not a fraction in a sentence. A checklist of what's measured →
  literal checkboxes, not a paragraph listing them.
- **Is there a project asset (an article's illustration, a diagram already made for other content)
  that already tells this exact story?** Check before commissioning or building something new - 
  reusing a real, on-brand illustration is both less work and more credible than an abstract
  substitute. When one is used, make sure the on-slide copy and the image reinforce the same point
  rather than the image just decorating unrelated text.
- **Does a new visual pattern already exist elsewhere in the deck that solves the same problem?**
  Before inventing a new layout for a text+image slide, check whether a prior slide already
  established a reusable component for it (e.g. a split text/image row) - reuse and extend that
  class rather than writing a near-duplicate. If reused twice, it's a real component: promote it to
  the theme's own shared style block once, don't keep copy-pasting the block per slide.
- **For a full-bleed background-image-with-text-overlay treatment**: check whether the image should
  instead be fully visible (not cropped behind a scrim) - a split layout (text one side, image
  `object-fit: contain` on the other, never cropped) usually serves an illustration better than an
  overlay, unless the image was specifically composed as a background.
- **Is a data-driven chart/curve/diagram computed from the real numbers, or eyeballed to roughly the
  right shape?** Plot each point from its actual value; never hand-draw a curve that merely looks
  plausible - see `implementation-gotchas.md`. When comparing two groups side by side, both must use
  identical category labels in identical order - a mismatched vocabulary between "before" and
  "after" is a data bug, not a style choice.
- **Does the visualization's sophistication match the audience, not just what's mathematically
  standard?** A log scale is the "correct" way to plot a power law, but is not intuitive to a general
  audience - a linear scale showing the real explosive shape can communicate the point better. If the
  deck's audience isn't technical, default to the more intuitive option and say why in one sentence,
  rather than silently picking the more rigorous one.

## 5. Dynamics and reveal pacing

- **Does the slide reveal all at once when it's actually making several distinct points in
  sequence?** Default to fragmenting a multi-beat argument; default to revealing all at once only
  when the content functions as a reference/map the audience should be able to glance back at as a
  whole (state explicitly why, per-slide, if choosing "all at once" for a non-trivial slide).
- **Do related elements fire together or wrongly split across separate clicks?** If two elements
  are meant to land as one beat (e.g. a headline and the diagram that explains it), they need to
  share a fragment wrapper or an explicit matching `data-fragment-index` - plain sequential
  `class="fragment"` elements each get their own separate click by default.
- **For any boxed/panelled fragment, does the `fragment` class sit on the element carrying the
  visible chrome (border/background/shadow), not just its inner content?** Marking only the contents
  renders the empty box from the slide's rest state - screenshot fragment index −1 (not the
  hash-loaded "everything revealed" default) for every changed slide with a panel/card component to
  catch this; see `implementation-gotchas.md`.
- **Would a custom entrance animation make the point better than a static reveal?** Concrete
  patterns worth reaching for when the content earns it: a value that starts wrong and visibly
  corrects itself (colour fade + a drawn strike-through line), a rise-and-fade for stacked
  supporting text instead of a flat opacity cut, a sequential delay so a caused effect visibly
  follows its cause rather than appearing simultaneously (`transition-delay`, not a second fragment
  click, when the two should feel connected within one beat).
- **Is a callback to an earlier slide's device *reinforcing* the point, or just decorative repeat?**
  Reusing a motif from earlier in the deck (a number, a phrase, a visual element) on a later slide
  that inverts or confirms it is a strong device *when the audience can plausibly still remember
  the original* - check that the callback slide's own copy makes the connection explicit rather
  than assuming the audience will spot it unaided.
