# Implementation Gotchas — Presentation Build

Real defects caught mid-build, captured so they don't get rediscovered. Populated by
`present-build-expert`'s capture ratchet (see `render.md`) — a genuine bug fixed during a build gets
offered for promotion here (shared across every theme/deck) or kept local to the theme's own
`design.md`. Follows the same per-topic-file convention as the rest of `b2/shared/design/`.

## reveal.js `ready` fires before `initialize().then()` resolves

`Reveal.initialize()` returns a promise, but the `ready` event can fire before that promise
resolves in some load orders. Code that depends on the deck being fully initialized (custom
JS/motion setup in a theme's `theme.js`) should not assume `initialize().then()` is the first
signal — listen for `ready` as well, or guard initialization code to run once regardless of which
fires first.

## SVG-in-flexbox clips `text-anchor` content

An inline SVG placed inside a flexbox container can clip text positioned with `text-anchor="middle"`
or `text-anchor="end"` — the flex item's computed size doesn't always account for text that extends
beyond the SVG's own bounding box in the anchor direction. Give the SVG explicit `overflow: visible`
or size the flex item independently of the SVG's intrinsic dimensions when text-anchored labels are
involved.
