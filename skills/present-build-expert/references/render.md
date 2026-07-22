# Render Workflow

The theme preamble in `SKILL.md` has already resolved which theme applies. This file covers
everything after that: ID lifecycle, the generate-vs-reconcile decision, sequential authoring, the
shared runtime, and the final report.

---

## Step 1 — Read inputs

Read, in full:
- `docs/presentations/{slug}/{slug}.md` — the deck
- `website/presentation-themes/{theme}/design.md` — the slide-component design contract
- `website/presentation-themes/{theme}/theme.css` and `theme.js` — what every slide styles against

If `docs/presentations/{slug}/work.md` exists, skim it for context but never pull content from it
directly into slides — it's raw material, not approved copy.

## Step 2 — ID backfill and reconcile decision

Read `references/reconcile.md` now and follow it. It backfills missing slide ids and determines
whether this is a full generate (`no-prior-build`) or a reconcile (prior build exists — classify
each slide as unchanged / changed / new / moved / removed).

## Step 3 — Generate (sequential, deck-wide)

Regardless of full-generate or reconcile, this step only touches slides classified **changed** or
**new** (a full generate means every slide falls into "new"). Author them **in one continuous
pass, in the deck's current order** — not one isolated call per slide — so the whole deck reads as
one coherent hand-crafted piece. This is a deliberate difference from `present-design-expert`'s
parallel-agent mockups: those 2-3 concepts are supposed to diverge from each other; this one deck
is not.

For each slide to generate:
- Use the theme's slide-component pattern for that slide's apparent type (title / section / content
  / data / image / closing — infer from its content, the mockup set isn't an exhaustive taxonomy)
  as the **starting contract**, not a rigid mold. Extend it with bespoke per-slide craft — a unique
  data visualization, a custom SVG illustration, a per-slide animation keyed to the slide's own
  content — wherever the slide's `<!-- Visual: ... -->` comment or content calls for it. Never
  settle for the generic template when the content deserves better; this is the whole point of the
  two-level model.
- Translate `<!-- Visual: ... -->` comments into real visual treatment: inline SVG/CSS-drawn
  graphics for diagrams/charts/abstract compositions; for photographic imagery, either use an asset
  already in `docs/presentations/{slug}/assets/` or `website/theme/{THEME}/assets/` (site-shared),
  or tell the user which slides would benefit from `/b2:illustrate` and let them decide rather than
  blocking the build on it.
- Fragments: markdown `<!-- .element: class="fragment" -->` on a source element carries straight
  through to the corresponding output element — reveal.js interprets `.fragment` natively, no
  translation needed.
- Speaker notes: the source `Note:` block becomes `<aside class="notes">...</aside>` inside the
  `<section>` — reveal.js's native notes-plugin marker, read by its speaker view.
- Slide/hidden attributes: `<section id="{id}" data-slide-id="{id}"` — always both; add
  `data-visibility="hidden"` verbatim when the source slide has it. This is the only handling
  hidden slides need — reveal.js does the rest (skip in linear flow/count, shown in presenter
  overview, promotable live).
- Apply the pacing/beat discipline from the theme's `design.md` — fragments reveal on the deck's
  natural beats, not a fixed tap rhythm.

For slides classified **unchanged** or **moved**: copy the existing `<section>` verbatim (moved
slides just relocate to their new position in the output order) from the current
`website/dist/presentations/{slug}/index.html` — do not re-author them, this is what preserves the
hand-crafted design across content edits elsewhere in the deck.

For slides classified **removed**: omit their `<section>` from the new output entirely.

## Step 4 — Assemble the output file

Write `website/dist/presentations/{slug}/index.html`: standard reveal.js shell (doctype, links to
`../shared/reveal/dist/reveal.css` + `../shared/themes/{theme}/theme.css` — `{theme}` is the name
resolved in the Theme Preamble, never a generic "the theme's CSS" — a `<div class="reveal"><div
class="slides">` containing every `<section>` in the current source's order, reveal.js init script
enabling the notes plugin, and a `<script src="../shared/themes/{theme}/theme.js">` tag only if
that file exists for this theme).

## Step 5 — Shared runtime

Two independently-lifecycled parts live under `website/dist/presentations/shared/`: reveal.js core
(`shared/reveal/`, identical across every theme and deck, vendored once) and per-theme assets
(`shared/themes/{theme}/`, one subfolder per theme, refreshed on every build). Do not conflate
them — a deck on theme B must never end up served by theme A's CSS, and a locked theme's CSS/JS
edits must reach every deck on it, not just the first one ever built.

**Reveal.js core (vendor once, reuse forever):**

```bash
root="$(pwd)"
if [ -z "$(ls -A "$root/website/dist/presentations/shared/reveal" 2>/dev/null)" ]; then
  mkdir -p "$root/website/dist/presentations/shared/reveal"
  version="5.1.0"
  curl -sL "https://registry.npmjs.org/reveal.js/-/reveal.js-${version}.tgz" -o /tmp/reveal.tgz
  tar -xzf /tmp/reveal.tgz -C /tmp
  cp -r /tmp/package/dist "$root/website/dist/presentations/shared/reveal/dist"
  cp -r /tmp/package/plugin "$root/website/dist/presentations/shared/reveal/plugin"
  rm -rf /tmp/reveal.tgz /tmp/package
fi
```

Self-hosted, not CDN — a live presentation must not depend on venue wifi to load its own runtime.
The npm registry tarball ships a pre-built `dist/` (no Node/build step required, consistent with
this plugin's no-`node`-assumed constraint). `version` is a pin, not a hard requirement — bump it
by hand if a newer reveal.js release is needed; this is unversioned in the sense that nothing here
tracks upstream automatically (per the plan's deferred `shared/v1/` versioning — revisit only once
multiple themes/decks are live and a breaking runtime change is actually needed).

**Per-theme assets (copy every build, unconditionally):**

```bash
root="$(pwd)"
theme="{theme}"  # substitute the resolved theme name
mkdir -p "$root/website/dist/presentations/shared/themes/$theme"
cp "$root/website/presentation-themes/$theme/theme.css" "$root/website/dist/presentations/shared/themes/$theme/theme.css"
[ -f "$root/website/presentation-themes/$theme/theme.js" ] && cp "$root/website/presentation-themes/$theme/theme.js" "$root/website/dist/presentations/shared/themes/$theme/theme.js"
```

Runs on every build regardless of whether `shared/reveal/` was already populated — cheap (a few KB
of CSS/JS), and it's what guarantees a theme redesign propagates to every deck on it the next time
any of them rebuilds, and that a second theme's assets actually exist in `dist/` at all. Copy any
theme-referenced assets (images, fonts) the same way, into
`shared/themes/{theme}/assets/`.

## Step 6 — Client variants and handouts

No special handling required. A client variant is just another slug — a copied
`docs/presentations/{variant-slug}/` folder, built with this same workflow, producing its own
independent `website/dist/presentations/{variant-slug}/`. The live presentation and the handout are
the same URL; reveal.js's speaker view is a client-side mode switch, not a separate build.

## Step 7 — Report

```
{slug}: {full generate | reconciled}
  Generated: N slides
  Preserved: N slides (unchanged)
  Relocated: N slides (moved)
  Removed: N slides
  IDs assigned: N (only if > 0)

Live at: website/dist/presentations/{slug}/index.html
Deep links: .../index.html#/{slide-id}
Presenter view: press 'S' once the deck is open (reveal.js built-in, no server required)
```

Offer to serve: "Want me to run `/b2:serve` to preview it? (yes/no)"
