# b2 Generic Design Foundation

Shared, b2-internal reference module holding the **generic** design concern — named things (libraries,
movements, systems, trends) plus design judgment — that b2's output-specific design skills draw on.
Load only the slice a phase needs; do not read the whole module at once (progressive disclosure,
token-lean).

> **Verify versions at build time; the web moves fast.** Every dated claim below (library pricing,
> framework versions, Baseline status) can age. Confirm before relying on it. Sources at the foot of
> this file.

## Consumers

| Skill | Uses | Status |
|-------|------|--------|
| `design-expert` (website design) | `web-design-principles.md` (always), plus per-phase slices | Now (this slice) |
| `present-design-expert` (presentation theme design) | `web-design-principles.md`, `interview-questions.md`, `styles-and-business.md`, `trends.md`, `animation-motion.md`, `3d-visual-effects.md`, `gallery-template.html` | Now (presentation slice) |
| `present-build-expert` (presentation render) | `implementation-gotchas.md` — read on capture-ratchet promotion decisions, written to when a bug is promoted from a theme's local `design.md` | Now (capture ratchet) |
| `illustrate-expert` | style/trend slices as needed | Optional, later |

`art-director` is a **bob** skill, not a b2 skill — it cannot read this module. See the boundary note.

## Index — load-when trigger words

| File | Load when | Trigger words |
|------|-----------|---------------|
| `web-design-principles.md` | **Always** (design-expert); evaluation (website-review) | hierarchy, typography, colour, whitespace, grid, Gestalt, interaction states, accessibility, b2 theme maintainability |
| `styles-and-business.md` | Direction proposals, business-fit mapping (Phase B2), grounding | minimalism, Swiss, editorial, bento, brutalism, maximalism, glassmorphism, dark-mode, retro/Y2K, organic, style→business fit |
| `animation-motion.md` | A page/slide needs motion; mockup animation decisions | GSAP, Motion, anime.js, WAAPI, View Transitions, scroll-driven CSS, Lenis, prefers-reduced-motion |
| `3d-visual-effects.md` | 3D/visual-effect is on the table | Three.js, R3F, drei, Babylon, Spline, WebGL, GLSL, Canvas 2D, when-3D-helps |
| `design-systems.md` | Tokens, component systems, framework choice | design tokens, DTCG, Style Dictionary, Tailwind v4, Material 3, Radix, shadcn, DESIGN.md |
| `trends.md` | "What's current", 2026 direction framing | tactile brutalism, bento matured, spatial UX, AI personalization, scrollytelling, kinetic type, native motion, OKLCH |
| `interview-questions.md` | Interview grounding (Phase A1), gaps-only questioning — SHARED design+present | business & goals, audience, brand & personality, competitive context, content & conversion, constraints |
| `presentation-design.md` | Presentation interview/mockups/theme-lock, always — presentation-specific discipline | stage typography, reading distance, pacing, beat philosophy, presentation psychology, curiosity gap, cognitive load, motion intensity ladder |
| `gallery-template.html` | Any skill generating mockup concepts for review — not a trigger-word reference file, a template consumed via direct path (`${CLAUDE_PLUGIN_ROOT}/shared/design/gallery-template.html`) | mockup gallery, concept review, index.html generation |
| `implementation-gotchas.md` | `present-build-expert`'s capture ratchet, before reporting — written to (not just read) when a genuine bug's fix is promoted from a theme's local `design.md` | reveal.js init timing, SVG/flexbox clipping, real defects found and fixed mid-build |


## bob/b2 boundary

This module is **b2-internal**. bob designs product/app UI independently via `bob:ui-design`, with no
website and no b2. The two plugins integrate only through well-known project files
(`docs/product/*`, `website/docs/decisions.md`), never by reading each other's internal files — and the direction
is one-way: bob may wrap b2's file outputs when co-installed, never the reverse. Any knowledge overlap
across the plugin boundary is the accepted cost of independence (independence > cross-plugin DRY). If
bob ever adopts the same fact base, vendor it from one dev-time source at release — do not merge the
plugins or add runtime plugin-detection.

## Sources (2026 claims)

- GSAP free: https://webflow.com/updates/gsap-becomes-free · https://gsap.com/pricing/
- Motion rename/merge: https://motion.dev/ · https://github.com/motiondivision/motion
- Tailwind v4 (Jan 22 2025, `@theme`): https://tailwindcss.com/blog/tailwindcss-v4
- View Transitions Baseline Oct 2025: https://web.dev/blog/same-document-view-transitions-are-now-baseline-newly-available · https://developer.chrome.com/blog/view-transitions-in-2025
- 2026 trends: https://studiomeyer.io/en/blog/webdesign-trends-2026-reality-check · https://fireart.studio/blog/the-best-web-design-trends/ · https://www.figma.com/resource-library/web-design-trends/
