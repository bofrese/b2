# Phase 3 - Iteration and Theme Lock

---

## Iteration

The user names a concept from the gallery. Make in-place edits to that `concept-N.html` based on
feedback (combine elements, adjust colour/type/motion) - same edit-in-place model as `design-expert`,
no new concept files spawned.

After each update, regenerate `website/presentation-mockups/index.html` (same procedure as the
mockup phase's "Generate the gallery" step) so the thumbnail and notes reflect the change.

After each update: "I've updated the concept and refreshed the gallery. Reopen
`website/presentation-mockups/index.html`. What else needs changing, or are you ready to lock this
in?"

Wait for explicit approval ("lock it in", "that's it", "approved") before proceeding - feedback
that also requests a change is not approval.

On approval, update `website/docs/status.md`:
```
  phase: lock
```

---

## Theme Lock

Ask for a theme name (default: derive from the direction name, lowercase-hyphenated - e.g. "Site,
Amplified" → `site-amplified`). If `website/presentation-themes/{name}/` already exists, ask
whether to overwrite (redesign) or pick a different name.

```bash
root="$(pwd)" && mkdir -p "$root/website/presentation-themes/{name}"
```

Extract from the approved concept HTML and write:

### `theme.css`

The concept's full `<style>` block, generalized from the fixed 6-slide sample set into reusable
slide-component classes (`.slide-title`, `.slide-section`, `.slide-content`, `.slide-data`,
`.slide-image`, `.slide-closing`, plus any shared tokens - colour variables, type scale, spacing
scale). This is the design contract `present-build-expert` applies when generating a deck's actual
slides - semantic, reusable, not a copy-paste of the mockup's literal markup.

**Two mockup-format assumptions that do not survive generalization - check both before locking:**

1. **No component's resting CSS may be `opacity:0`.** The mockup is a continuous scroll animated by
   GSAP ScrollTrigger; a real deck is reveal.js, paginated via `class="fragment"` - nothing ever fires
   ScrollTrigger there, so anything hidden by default in `theme.css` stays invisible forever. Every
   component defaults to visible; staged reveals are the *deck's* job via reveal.js's native
   `.fragment`, never baked into the theme.
2. **Any shared "slide shell" rule must be scoped to an element type, never a bare class/attribute
   selector.** `[class^="slide-"]` also matches reveal.js's own internal elements
   (`.slide-background`, `.slide-number`) and corrupts its scale-to-fit/centering math - invisible at
   the deck's native aspect ratio, breaks visibly at any other one. Use `section[class^="slide-"]`.

Full detail and why these matter in `${CLAUDE_PLUGIN_ROOT}/shared/design/implementation-gotchas.md`.

### `theme.js`

Any shared JS the concept used (motion/3D setup, reveal-event hooks). Keep bespoke per-slide
animation logic out of this file - that gets authored per-deck by `present-build-expert`; this file
holds only what's genuinely shared across every deck using this theme (e.g. a shared GSAP timeline
helper, a shared Three.js scene setup function).

### `design.md`

A slide-oriented design guide, parallel to the website's `theme/{THEME}/design.md`:

```markdown
# {Theme Name} - Presentation Design Guide

## Visual Identity
{1-2 sentences - how this theme extends the website's design language for the stage}

## Motion Intensity
{minimal / moderate / dynamic, and what that means concretely for this theme}

## Colour System
{colours + roles, inherited from website/theme/{THEME}/design.md with stage-contrast adjustments noted}

## Typography System
{headline/body fonts + stage-scaled sizes - larger than the website's scale, with reasoning}

## Slide Component Patterns
### Title / Opening
### Section / Agenda
### Content + Bullets
### Data / Chart
### Image-Forward
### Closing / CTA
{1-2 sentences each - the layout logic present-build-expert should follow for that slide type}

## Anti-Patterns
{what this theme should never do - e.g. "never more than 3 bullets," "never a static data slide if motion intensity is dynamic"}
```

### `preview.css`

A simplified subset of `theme.css` for the Obsidian Slides Extended preview - same colour/type
tokens, no bespoke per-slide JS/motion (Obsidian's preview is a quick visualization, not the real
build; see `docs/domain/presentation-architecture.md`).

**One-time Obsidian setup note (first theme only):** if this is the first theme locked in this
project, tell the user:

> "One-time Obsidian setup: open Slides Extended's plugin settings and set its 'Assets directory'
> to `website/presentation-themes/`. Every theme's `preview.css` lives there, and a deck's `theme:`
> frontmatter selects which one previews - you only need to set this once, even as you add more
> themes later."

Skip this note on a second or later theme in the same project (already set up).

### Root-relative paths in theme.css / theme.js

Any path `theme.css` or `theme.js` reference (fonts, images, other assets) must be root-relative
(`/theme/...` style), never a relative path (`../assets/...`). Theme files get copied to multiple
directories across the build pipeline (`website/presentation-themes/{name}/` → per-build into
`website/dist/presentations/shared/themes/{name}/`) - a relative path resolves differently at each
copy location and silently breaks after the first copy.

### Verification (before Report)

Runs once per theme lock - not on every later rebuild of a deck using this theme.

Resolve a real deck to verify against:

```bash
root="$(pwd)" && ls -t "$root/docs/presentations/"*/*.md 2>/dev/null
```

- **Exactly one deck exists** (or one was created earlier this session) → use it.
- **Multiple decks exist** → ask the user which one to verify against.
- **None exist** → skip the smoke-test/diff step below entirely (there is nothing real to build).
  Still write `theme.css`/`theme.js`/`design.md`/`preview.css` as above - none of those need real
  content. Tell the user in the Report: "Theme locked, but not yet verified against a real build - 
  run `/b2:present` to write a deck, then `/b2:present-build` will verify against this theme
  automatically on first render."

**When a real deck is available:** use the Skill tool to invoke `present-build-expert`, passing that
deck's slug, to build it for real against this just-locked theme. Then diff computed styles between
the approved mockup concept (`website/presentation-mockups/concept-N.html`, the one that was locked)
and the freshly-built real deck (`website/dist/presentations/{slug}/index.html`) - sample the shared
tokens both should agree on (type scale, colour variables, spacing scale) via one batched
`browser_evaluate` call across a couple of comparable slide types (e.g. the title slide and one
content slide in each). Report any material divergence (this is what would have caught the 2.6×
font-size bug from an un-inherited base theme) before the lock is considered done - if a divergence
is found, fix `theme.css` and re-verify before reporting.

### Report

Tell the user:

```
Theme locked: website/presentation-themes/{name}/

Any presentation can now use it - set `theme: {name}` in its frontmatter, or let
/b2:present-build resolve it automatically if it's your only theme.
```

If verification ran: report the sampled values it compared and confirm they matched (or what was
fixed). If verification was skipped (no real deck yet): include the "not yet verified" note from
above.
