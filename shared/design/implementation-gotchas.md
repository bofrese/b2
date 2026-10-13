# Implementation Gotchas - Presentation Build

Real defects caught mid-build, captured so they don't get rediscovered. Populated by
`present-build-expert`'s capture ratchet (see `render.md`) - a genuine bug fixed during a build gets
offered for promotion here (shared across every theme/deck) or kept local to the theme's own
`design.md`. Follows the same per-topic-file convention as the rest of `b2/shared/design/`.

## reveal.js `ready` fires before `initialize().then()` resolves

`Reveal.initialize()` returns a promise, but the `ready` event can fire before that promise
resolves in some load orders. Code that depends on the deck being fully initialized (custom
JS/motion setup in a theme's `theme.js`) should not assume `initialize().then()` is the first
signal - listen for `ready` as well, or guard initialization code to run once regardless of which
fires first.

## SVG-in-flexbox clips `text-anchor` content

An inline SVG placed inside a flexbox container can clip text positioned with `text-anchor="middle"`
or `text-anchor="end"` - the flex item's computed size doesn't always account for text that extends
beyond the SVG's own bounding box in the anchor direction. Give the SVG explicit `overflow: visible`
or size the flex item independently of the SVG's intrinsic dimensions when text-anchored labels are
involved.

## A theme's shared "slide shell" rule must target what the generated markup actually carries

Mockups often use two classes (`class="slide s-title"` - shared base + type modifier). Generalizing
to single semantic classes (`class="slide-title"`) orphans any shell CSS still written against the
literal `.slide` selector - it matches nothing, every slide shrinks to fit its own content instead
of filling the canvas. Fix: target the common prefix, not a literal class - but **scope it to the
element type** (see next entry, this was fixed twice).

## Scope prefix/attribute selectors to an element type when the runtime has its own class names

`[class^="slide-"]` (no element type) doesn't just match a theme's own slide-type classes - in a
reveal.js deck it also matches reveal's *own internal* elements (`.slide-background`,
`.slide-background-content`, `.slide-number`), none of which are `<section>`. Forcing
`position/display/height` (even `!important`) onto those internal layout divs corrupts reveal's own
scale-to-fit and centering math. It's invisible at the deck's exact configured canvas size and only
breaks (off-centre, content cut off) at any other aspect ratio - e.g. fine on a 16:9 laptop, broken
on an iPad. Fix: `section[class^="slide-"]` - every real slide type is always a `<section>`; reveal's
internals never are. **Test at a non-native aspect ratio** (see verification entry below) or this
stays invisible until a user reports it from a real device.

## reveal.js's own `.slides>section.present{ display:block }` rule outranks a plain theme class

Specificity (0,3,1) - a theme's own shell rule for slide layout (e.g. `display:flex` to centre
content) loses that fight if written as a bare class/attribute selector, and reveal's `display:block`
silently wins. Fix: the theme's `display`/`height` overrides for the slide shell need `!important` - 
a deliberate, narrow, documented override of a known third-party rule, not a general escape hatch.

## Verify a reveal.js build at a non-native aspect ratio, not just its configured canvas size

Both selector bugs above were invisible when checked only at the deck's own `width`/`height`
(reveal.js's scale-to-fit math happens to degenerate to a no-op there). Resize the browser to at
least one different aspect ratio (e.g. an iPad landscape, ~4:3) before calling a reveal.js build
verified - cheap, and it's the only way these two classes of bug actually surface in testing instead
of in front of the user.

## A `.fragment`'s resting state must not assume a specific runtime will animate it in

A component authored for a scrolling mockup (GSAP ScrollTrigger clears its `opacity:0` on scroll)
silently breaks if reused as-is inside a real reveal.js deck - reveal.js paginates via
`class="fragment"` (its own `opacity:0` → `.visible{opacity:1}`, unrelated to scrolling), so nothing
ever clears a component-level `opacity:0`. Fix: components default to visible; staged reveals are
opt-in per element via reveal.js's native `.fragment`, never baked into a shared component's resting
CSS.

## Verify a reveal.js build by stepping fragments and reloading cold, not just checking rest-state

Two ways a check can pass while the deck is actually broken: (1) inspecting a slide's *resting*
DOM state without advancing its fragments - a `.fragment` stuck permanently hidden reads the same as
"not yet revealed" until you actually step through it; (2) re-navigating via a hash change on an
already-loaded page, which reuses the current DOM/JS state and can mask a bug that only reproduces on
a genuine cold load. Verify by advancing every fragment at least once, and by doing a real full
navigation (not a `#/hash`-only one) after any change to `theme.css`/`theme.js`.

## A pure-`vw` `clamp()` on multi-line display type doesn't respond to window height

A large headline sized only with `vw` units (no `vh` term) scales correctly as a window gets
narrower or wider, but is blind to height - on a wide-but-short window (e.g. 1440×900) a 3-line
display headline can outgrow the slide's own box and get cropped top and bottom by the shell's
`overflow:hidden`. Invisible at any window where width and height both happen to be generous, which
is exactly the window most authoring and casual testing happens in. Fix: use `min(Xvw, Yvh)` for the
clamp's middle term so the size responds to whichever dimension is actually the tighter constraint - 
already the established pattern for shorter components in this codebase (list items, table rows);
apply the same fix to large display headlines, which are more likely to hit this because they're
tall by design. Test any big display headline at a short-but-wide window specifically, not just a
generic "different aspect ratio" check.

## Don't cap a line's `max-width` narrower than the sibling line(s) it visually belongs with

A closing or supporting line of text that's meant to read as part of the same block as the text
above it (a blockquote, a headline) needs the same effective wrap width as that text - not a
separately-chosen "looks about right" narrower value. A narrower cap can orphan the last word or two
onto their own line even though the line above clearly had room, and it's easy to miss because the
narrower box still *looks* deliberate in isolation - the defect only shows up compared against its
neighbour. Check wrap points specifically wherever a short closing line sits under a longer,
wider element it's meant to pair with.

## `curl`/checksum the served bytes before re-debugging code that "should already be fixed"

A fix that doesn't visibly take effect after a browser reload - even with the browser's cache
disabled in devtools - is not proof the code is still wrong. Live-reload dev-server injection,
hash-only navigation reuse, and HTTP caching layers between origin and browser have all produced
this exact symptom in this project. Compare the served response (`curl | md5`) against the file on
disk before assuming the fix itself failed.

## A fixed px value "fixing" an unbalanced layout usually relocates the bug, not removes it

`width:42%`/`min-width:340px` on one side of a split forces the other side to absorb 100% of any
extra viewport width - patching that with a second fixed `min-width` on the starved side just moves
the dead-space bug to whichever side doesn't have a floor. Any layout complaint shaped like "column A
is cramped, column B has empty space" needs a proportional fix (`flex-grow` ratios, i.e. flexbox's
`fr`-unit equivalent - `flex:3 1 0` / `flex:2 1 0` for a 60:40 split), not a px value tuned to look
right at one specific viewport width. Same root cause as the `vw`-only clamp entry above: a fixed
unit "working" at the window it was authored on and failing everywhere else.

## Group a boxed/panelled fragment by its container, not just its contents

Marking a panel's *children* `class="fragment"` while leaving the panel's own border/background
unmarked renders the empty box (border, fill, drop shadow) from the slide's resting state - reads at
a glance like "nothing's there yet" because it's visually empty, but the shell is already on screen
before its beat fires. The fragment class belongs on whichever element actually carries the visible
chrome (border/background/shadow), not on the innermost text node. **Screenshot every changed slide's
true resting state (fragment index −1, not just the hash-loaded "everything revealed" default) for
any slide with a boxed or panelled component** - this class of bug is invisible in the final-state
screenshot and only shows up at rest.

## A component with its own centering/max-width must be a direct child of the slide, not nested a level deeper

A two-column or grid component that sets its own `max-width` + `margin:0 auto` stops growing past
whatever width its *parent* container caps it to - if that parent is itself a narrower single-column
wrapper (built for a different, one-column slide pattern), the component silently plateaus at the
parent's cap on every viewport, and no per-column ratio fix inside the component can compensate for
it. This reads identically to the "fixed px value" bug above (dead space on one side that widening
the window doesn't fix) but the actual defect is one level up in the DOM, not in the component's own
CSS - check the component's *ancestor chain* for a competing width constraint before re-tuning the
component itself.

## Verify a data-driven graphic against its real numbers, not by eye

A hand-drawn SVG curve/bar/bezier that merely *looks* like the right shape for the underlying data
drifts from being technically wrong (points don't actually lie on the curve, axis positions are
guessed) in a way that's easy to ship because it still reads as plausible at a glance. Compute each
plotted point's coordinate from the real formula/dataset and place it exactly - never eyeball a curve
shape and drop labels near it. Where the same dataset is split into comparable groups (e.g. a
before/after, an A/B), use identical category labels in identical order on every side - a mismatched
vocabulary (one side says "Snake", the other says "Reptile" for the same category) is a data-integrity
bug, not a style choice, and needs the same explicit check as any other build verification step.
