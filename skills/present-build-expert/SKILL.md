---
name: present-build-expert
description: This skill should be used when the user runs "/b2:present-build", asks to "render my
  presentation", "build the deck", "publish the presentation", "update the live deck", or wants
  `docs/presentations/<slug>/<slug>.md` turned into (or updated at)
  `website/dist/presentations/<slug>/index.html`. Applies a locked presentation theme, generates or
  surgically reconciles the rich per-slide HTML, and manages the shared reveal.js runtime.
---

# b2 Present Build Expert

Act as the craftsperson who takes a locked theme and a content deck and produces the actual
bespoke, presentable HTML — the layer where hand-crafted per-slide design lives. Runs per deck, on
demand, never automatically as part of a routine site rebuild.

---

## Prerequisite: resolve the slug

The user names a deck (slug, title, or path). Resolve to `docs/presentations/{slug}/{slug}.md`. If
it can't be found, ask for the slug directly. If the folder exists but has no `.md` file matching
its own name, tell the user and stop — this isn't a state `/b2:present` create mode should ever
leave.

## Theme Preamble

Read the deck's frontmatter `theme:` field.

- **Set and the theme folder exists** (`website/presentation-themes/{theme}/`) → use it.
- **Set but the folder doesn't exist** → treat as unset (stale reference) and fall through below.
- **Unset:**
  ```bash
  root="$(pwd)" && ls "$root/website/presentation-themes/" 2>/dev/null
  ```
  - Zero themes → halt: "Run `/b2:present-design` first — there's no presentation theme to build
    with yet."
  - One theme → use it silently, write its name into the deck's `theme:` frontmatter (Edit tool),
    mention it: "Using your `{name}` presentation theme."
  - Multiple themes → ask which one, defaulting to the most recently created (by directory mtime:
    `ls -t "$root/website/presentation-themes/"`). Write the chosen name into `theme:`.

## Workflow

Read `references/render.md` and follow it — it covers ID backfill, the stale/reconcile decision,
sequential generation, shared-runtime management, and client-variant/hidden-slide handling.

## References

- **`references/render.md`** — the full build workflow (main entry point for this skill's logic).
- **`references/reconcile.md`** — the git-diff-based per-slide-id reconcile algorithm, loaded by
  `render.md` when a prior build already exists.
