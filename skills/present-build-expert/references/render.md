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

**Report scope before proceeding on a full generate:** slide count, and how many carry a
`<!-- Visual: -->` comment implying bespoke craft (chart, diagram, sequence, etc.). A "verify the
theme against a real deck" ask is not the same request as "build this deck" — a 40+ slide talk with
several custom diagrams is a materially different commitment than sampling 2–3 slides, and the user
should choose that scope explicitly rather than discover it mid-build.

## Step 2 — ID backfill and reconcile decision

Read `references/reconcile.md` now and follow it. It backfills missing slide ids and determines
whether this is a full generate (`no-prior-build`) or a reconcile (prior build exists — classify
each slide as unchanged / changed / new / moved / removed).

## Step 3 — Assemble incrementally while generating (sequential, deck-wide)

**Assembly is now driven by this step, not a separate end-of-pass write** (Step 4 below only
finalizes). Before processing any slide, write the shell once:

```bash
root="$(pwd)"
slug="{slug}"  # substitute actual slug
theme="{theme}"  # substitute the resolved theme name
mkdir -p "$root/website/dist/presentations/$slug"
```

Write `website/dist/presentations/{slug}/index.html` with the standard reveal.js shell — doctype,
links to `../shared/reveal/dist/reveal.css` + `../shared/themes/{theme}/theme.css` (`{theme}` is the
name resolved in the Theme Preamble, never a generic "the theme's CSS"), an **empty**
`<div class="reveal"><div class="slides"></div></div>`, reveal.js init script enabling the notes
plugin, and a `<script src="../shared/themes/{theme}/theme.js">` tag only if that file exists for
this theme. The empty `<div class="slides"></div>` is the anchor every subsequent slide insertion
targets.

Then process every slide **in one continuous pass, in the deck's current order** — not one isolated
call per slide — so the whole deck reads as one coherent hand-crafted piece, and so each slide's
`<section>` is appended to the output immediately once it's ready (via Edit, replacing
`</div></div>` with `  <section>...</section>\n  </div></div>` — i.e. insert before the closing
anchor, then that becomes the new anchor for the next slide). This is a deliberate difference from
`present-design-expert`'s parallel-agent mockups: those 2-3 concepts are supposed to diverge from
each other; this one deck is not.

Regardless of full-generate or reconcile, only slides classified **changed** or **new** get authored
(a full generate means every slide falls into "new"). For each slide to generate:
- Use the theme's slide-component pattern for that slide's apparent type (title / section / content
  / data / image / closing — infer from its content, the mockup set isn't an exhaustive taxonomy)
  as the **starting contract**, not a rigid mold. Extend it with bespoke per-slide craft — a unique
  data visualization, a custom SVG illustration, a per-slide animation keyed to the slide's own
  content — wherever the slide's `<!-- Visual: ... -->` comment or content calls for it. Never
  settle for the generic template when the content deserves better; this is the whole point of the
  two-level model.
- **Visual-first collaboration** (see below) runs here, before the slide's section is finalized and
  appended.
- Translate `<!-- Visual: ... -->` comments into real visual treatment: inline SVG/CSS-drawn
  graphics for diagrams/charts/abstract compositions; for photographic imagery, either use an asset
  already in `docs/presentations/{slug}/assets/` or `website/theme/{THEME}/assets/` (site-shared),
  or tell the user which slides would benefit from `/b2:illustrate` and let them decide rather than
  blocking the build on it.
- Fragments: markdown `<!-- .element: class="fragment" -->` on a source element carries straight
  through to the corresponding output element — reveal.js interprets `.fragment` natively, no
  translation needed.
- Speaker notes: the source `Note:` block becomes `<aside class="notes">...</aside>` inside the
  `<section>` — reveal.js's native notes-plugin marker, read by its speaker view. Preserve the
  keyword-bullets-then-prose structure from `slide-format.md` as-is inside the `<aside>` — no
  translation needed, it's plain text either way.
- Slide/hidden attributes: `<section id="{id}" data-slide-id="{id}"` — always both; add
  `data-visibility="hidden"` verbatim when the source slide has it. This is the only handling
  hidden slides need — reveal.js does the rest (skip in linear flow/count, shown in presenter
  overview, promotable live).
- Apply the pacing/beat discipline from the theme's `design.md` — fragments reveal on the deck's
  natural beats, not a fixed tap rhythm.

For slides classified **unchanged** or **moved**: append the existing `<section>` verbatim (moved
slides just relocate to their new position in the output order) from the current
`website/dist/presentations/{slug}/index.html` — do not re-author them, this is what preserves the
hand-crafted design across content edits elsewhere in the deck. (Read that section's markup before
Step 3 overwrites the file with the new shell, since the old file is about to be replaced.)

For slides classified **removed**: skip them — never append their `<section>`, and (no-git path
only) confirm with the user first per `reconcile.md`.

### Visual-first collaboration + `.md` sync

Default mode: **per-slide interactive**. For each slide being generated (new/changed only — copied
unchanged/moved slides skip this, they're not being re-authored):

1. If a visual could carry the message with less text, propose it.
2. Append the candidate section as described above, then tell the user: "Updated slide '{id}' —
   refresh and jump to `.../index.html#/{id}`. Like it, or adjust?" (Requires the user to have a
   local server running and the deck open, e.g. via `/b2:serve` — if the build hasn't offered that
   yet this session, offer it now before the loop starts.)
3. Reject/adjust → replace that same section (Edit, matching its `id`) with the next candidate,
   repeat.
4. Accept → move any text displaced by the visual to the top of that slide's notes (bullets-then-
   prose format per `slide-format.md`), and write the same content into the source `.md` — **one
   accept covers both files**. No separate sync-permission prompt; the accept itself is the
   permission, since the user is looking at the actual rendered result before saying yes.
5. Move to the next slide.

Two alternate modes, offered once up front (not re-asked per slide): **batch** (all proposals shown
as one list, one approval round) and **passive** (no proposals, only on explicit request). In both,
an approval still triggers the same three-part bundle (apply visual + move text to notes + sync
`.md`) — only the proposal/approval timing differs from the default mode.

### Capture ratchet

During this step, silently track any **genuine bug** fixed while authoring a slide (a real defect —
wrong values, race conditions, broken layout — not a style/taste preference). No interruption
mid-build; the batched ask happens before the Step 7 report (see below).

### Theme cross-sync

While authoring a slide, if its need looks like a theme-level gap rather than a one-off bespoke
tweak: grep `theme: {name}` across `docs/presentations/*/*.md` frontmatter to count decks on this
theme.

- **Only this deck uses the theme** → judge and apply directly to the theme files (no permission ask
  — blast radius is provably zero), subject to the Tier 3 verification check below before reporting
  done (this path is one of the cases where a human hasn't reviewed the change live).
- **2+ decks use the theme** → ask before touching shared theme files.

## Step 4 — Finalize

By the time every slide has been processed in Step 3, `website/dist/presentations/{slug}/index.html`
is already complete — every `<section>` was appended in the current source's order as it was
generated or copied forward, and removed slides were never appended. This step is a checkpoint, not
a rewrite: confirm every slide id in the current source appears exactly once in the output, in the
source's order, and that no removed id remains. No full-file write happens here.

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

## Step 6.5 — Verification

Reuses the same browser-detection order `ui-review-expert` already has (MCP → `npx playwright` →
CLI → halt) — no new tooling. Gated by the slide classification already computed in Step 2 — no new
detection logic. Evidence lives in the report text itself (Step 7), not a separate artifact. Reuses
whichever local server is already running from the Step 3 collaboration loop, or starts one now if
none was needed this build (e.g. a fully passive-mode or no-interactive-slides run).

- **Tier 1 (always, cheap, deck-size-independent):** one `browser_evaluate` call that
  programmatically drives reveal.js through every slide (`Reveal.slide(i)` in a loop, inside the one
  call), collecting console errors across the whole deck. Do this after a genuine full navigation
  (`page.goto`, not a `#/hash`-only change) — a hash-only nav reuses the already-loaded DOM/JS and can
  mask a bug that only reproduces on cold load. Include at least one pass that steps every fragment on
  a slide forward (`Reveal.next()` repeatedly, or `Reveal.slide(i, 0, lastFragment)`), not just its
  resting state — a fragment stuck permanently hidden looks identical to "not yet revealed" until
  actually advanced.
- **Tier 1b (always, cheap): resize to one non-native aspect ratio** (e.g. an iPad landscape,
  ~4:3 — the deck's own configured `width`/`height` is 16:9 and will not exercise this) and repeat the
  slide sweep. reveal.js's scale-to-fit/centering math only does real work off its native canvas
  size — a broken shell selector or a `!important` fight with reveal's own CSS is invisible at the
  native size and only surfaces as off-centre/cut-off content at any other ratio. See
  `implementation-gotchas.md` for two real bugs this specifically caught.
- **Tier 2 (always, cheap):** one screenshot of reveal.js's built-in Overview mode
  (`Reveal.toggleOverview()`) — a full-deck visual sanity pass in a single shot.
- **Tier 3 (gated, expensive):** for slides classified new/changed *and* carrying a
  `<!-- Visual: -->` treatment, a custom illustration/SVG, or timing/animation properties — one
  full-resolution screenshot at **fragment index −1 (rest state)**, not just the hash-loaded
  "everything revealed" default (a boxed/panelled fragment whose chrome isn't itself marked
  `fragment` renders visible at rest — invisible unless rest state is actually screenshotted; see
  `implementation-gotchas.md`) + one batched computed-style/animation-sampling `evaluate` (timing
  properties sampled at N timestamps via `requestAnimationFrame`/`setTimeout` in one call, no
  per-frame screenshots), scoped to just those slides. **Skip entirely for slides that went through
  the default per-slide interactive propose/accept loop** — the user's live accept already is the
  verification. Apply Tier 3 only when no human reviewed the rendered result this build: batch mode,
  passive mode, or the theme cross-sync single-deck-on-theme auto-apply path. A changed slide that's
  a pure text edit (no visual comment touched, no new layout) skips Tier 3 regardless of mode.
- **Structural check (always, cheap, part of Tier 1):** any component with its own centering/
  `max-width` (a `.split`, grid, or comparison layout) must be a direct child of the slide, not
  nested inside a narrower single-column wrapper built for a different pattern — that silently caps
  the component at the wrapper's width on every viewport. Grep the generated markup for this before
  reporting a slide done, don't rely on catching it visually at one window size.
- **Data-consistency check (always, cheap):** for any slide comparing two or more groups (before/
  after, A/B, two chart series), confirm every group uses identical category labels in identical
  order, and confirm any plotted chart's points are computed from the actual data, not eyeballed —
  see `implementation-gotchas.md`.
- **Content-discipline checklist** (per slide touched this build): what is this slide's one core
  claim — does the illustration state it, or does the text restate what the illustration already
  shows?

If Tier 3 finds a material defect, fix it and re-run that slide's Tier 3 check before reporting.

## Capture-ratchet ask

If any genuine bugs were tracked silently during Step 3, ask once per entry before the report: "Fix
found: {one-line description}. Keep it local to this theme's `design.md` Anti-Patterns section, or
share it with every theme via `${CLAUDE_PLUGIN_ROOT}/shared/design/implementation-gotchas.md`?"

- **Local** → append to `website/presentation-themes/{theme}/design.md`'s `## Anti-Patterns` section.
- **Shared** → read `${CLAUDE_PLUGIN_ROOT}/shared/design/implementation-gotchas.md` first (skip if
  an equivalent gotcha is already documented there), then append. If the write fails (plugin
  directory not writable), tell the user the promotion couldn't be written and fall back to
  appending it locally instead, so the entry isn't lost.

## Step 7 — Report

```
{slug}: {full generate | reconciled}
  Generated: N slides
  Preserved: N slides (unchanged)
  Relocated: N slides (moved)
  Removed: N slides
  IDs assigned: N (only if > 0)

Verification: Tier 1 (console) clean | N console error(s) — {detail}
              Tier 2 (overview) — {any visible anomaly, or "clean"}
              Tier 3 ({N} slide(s) checked) — {clean, or defects found+fixed}

Live at: website/dist/presentations/{slug}/index.html
Deep links: .../index.html#/{slide-id}
Presenter view: press 'S' once the deck is open (reveal.js built-in, no server required)
```

Offer to serve: "Want me to run `/b2:serve` to preview it? (yes/no)"
