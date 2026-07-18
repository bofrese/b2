# Design systems & token approaches

Activation index. Named thing + terse when/why. Not a tutorial. **Verify versions at build time.**

- **Design tokens (W3C DTCG format)** — standardized JSON schema (`$value`/`$type`) for color/space/type/etc. Reach for: cross-platform/multi-brand source of truth, tool interop (Figma ↔ code).
- **Style Dictionary** (Amazon) — transforms token JSON → platform outputs (CSS vars, iOS, Android, JS). Reach for: multi-platform token pipelines.
- **Tailwind v4** (Jan 2025) — **CSS-first config via `@theme` directive** (no more `tailwind.config.js`); tokens = CSS variables; Rust "Oxide" engine, ~5x faster. Reach for: utility-first velocity; `@theme` doubles as your token layer.
- **Material Design 3 (Material You)** — Google's system; dynamic color, tonal palettes, expressive components. Reach for: Android-adjacent, Google-ecosystem, or when a complete opinionated system is wanted.
- **Radix UI** — unstyled, accessible headless primitives (menus, dialogs, popovers). Reach for: correct a11y/keyboard/focus behavior, bring your own styling.
- **shadcn/ui** — copy-in (not npm dep) components = Radix + Tailwind you own and edit. Reach for: React apps wanting ownership over a locked black-box lib. Dominant 2025-26 pattern.
- **DESIGN.md / markdown design-system convention** — human+AI-readable single-file design spec (tokens, voice, spacing, do/don't). Reach for: AI-driven design consistency, lightweight teams, feeding an agent its own guardrails.
