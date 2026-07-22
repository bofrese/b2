# Command Reference
*Last verified: 2026-07-16*

Every `/b2:*` command is a thin dispatcher onto a skill of the same name (e.g. `/b2:vision` invokes the `b2:vision-expert` skill) — the command file itself carries only a description and allowed tools. Listed here in the order you'd typically use them: orchestrator, exploration, one-time setup phases, then ongoing maintenance.

## `/b2` — Orchestrator

Run any time. Detects setup state from file existence (`docs/product/vision.md`, `website/docs/content-types.md`, entries in `website/docs/status.md`, `website/b2.cfg`) and outputs a status table plus exactly one recommended next command during setup. After all phases are complete it switches to maintenance mode and lists ongoing options instead. Also answers "what is b2" / "how does b2 work" directly from the plugin's internal knowledge file.

## `/b2:talk` — Exploration

Not a setup phase — usable any time, before or during any other step. Communication-strategist persona: pushes back on vague answers, extracts concrete stories and positioning. Saves to `docs/notes/README.md` and per-category files, which every setup command reads automatically if present. Optional, but reduces how much later interviews have to ask.

## `/b2:vision` — Vision

First step. Structured interview on purpose, audience, and success criteria, using reality-check questions — it presses for past behavior and concrete facts, not hypotheticals about the future.

**Produces:** `docs/product/vision.md`, `website/docs/status.md` (created here).

## `/b2:brand` — Brand

Interview covering name, tagline, competitive positioning, tone of voice (three adjectives, tested against real scenarios), a primary call-to-action forced to a single choice, and what the site deliberately won't say.

**Produces:** `docs/product/website-design-brief.md` (human-readable record), `website/docs/decisions.md` (terse voice guide every later AI-driven command reads).

## `/b2:structure` — Structure

Information architecture interview: pages, content types, navigation, user journey.

**Produces:** `website/docs/content-types.md`, page subfolders, stub `.md` files for each planned page.

## `/b2:write` — Write

World-class-copywriter persona. Reads `website/docs/decisions.md` for voice. Harvests existing material first (a URL, a file, or pasted text), proposes an outline, and waits for approval before writing. Places output in the correct `website/src/` path with correct frontmatter. Used once per stub page during setup, and again any time you add or revise a page. Offers to run a build afterward.

## `/b2:design` — Design

The most involved command. Five phases: interview → written design brief (needs your approval) → three concurrent HTML mockup concepts → iteration on your pick → theme generation. Mockups may use any CDN library, web font, or animation — no dependency whitelist; whatever the chosen mockup uses gets carried whole into the theme. Asks for a theme name (written to `website/b2.cfg` as `THEME=`). If a theme already exists (redesign), the existing semantic-class vocabulary is offered to the mockup agents as a soft reuse hint, not a constraint.

**Produces (under `website/theme/{name}/`):** `styles.css`, `components.md` (the semantic-class contract between theme and content — every class `/b2:sync` may use must be listed here), `header.html`, `footer.html`, `scripts.js`, `design.md` (includes image size specs used by SEO and review). Also `website/mockups/` (the three concepts plus a self-contained gallery `index.html`).

## `/b2:sync` — Sync

Converts stale `.md` source files into semantic HTML partials. The only AI-calling step in the day-to-day maintenance loop.

1. Detects stale files via git history, falling back to file timestamps.
2. For each stale file: reads the source, the existing partial (if any), `components.md`, `content-types.md`, and `website/docs/decisions.md`, then converts.
3. Regenerates index files for any content type with a stale item.
4. If a partial already exists, integrates changes surgically — preserves structure rather than regenerating from scratch.
5. Detects theme-vocabulary drift after a redesign and re-evaluates existing partials against the new `components.md` rather than requiring a full manual re-sync.

**Produces:** `website/partials/*.html`.

## `/b2:setup` — Technical Setup

Final one-time setup step, run after `/b2:sync`. Detects the build tool (a `website/Makefile` if present, otherwise the plugin's bundled scripts), asks whether the site lives at a root domain or a subdirectory (patches nav `href`/`src` in `header.html`/`footer.html` if not root), writes `website/b2.cfg`, creates any missing required folders, and runs the first build. Reports success or diagnoses a build failure — does not auto-fix Makefile issues.

**Produces / updates:** `website/b2.cfg` (`BUILD_TOOL=`, `BASE_PATH=` added; `THEME=` preserved from `/b2:design`).

## `/b2:build` — Build

The recommended day-to-day entry point. Runs stale-file detection, calls `/b2:sync` if anything is stale, then assembles `website/dist/` (via `make` or the bundled scripts, whichever `b2.cfg` names). Flags newly-created or significantly-changed pages for `/b2:website-review`, but doesn't force it.

**Produces:** `website/dist/`.

## `/b2:serve` — Local Server

Starts a local server on `website/dist/`, default `http://localhost:8099`. Tries Python 3, then `npx serve`, then Docker Compose (if `website/docker-compose.yml` exists), in that order. Before starting, checks whether something is already bound to the port and — rather than assuming it's fine or silently killing it — verifies it's actually serving this site's `dist/` before reusing it.

## `/b2:website-review` — Visual Review

Requires the server running (`/b2:serve` first). Screenshots pages via Playwright and evaluates them against the design system (`components.md`, `mockup.html`, `website/docs/decisions.md`) plus art-director-level judgment — a page can pass class-compliance and still be flagged as visually flat. Fixes layout issues directly in `website/partials/`. Also runs a per-page bespoke art-direction pass, proposing reskins, new reusable components, or illustration ideas — these are presented for confirmation, never auto-applied.

## `/b2:seo` — SEO

Full audit-and-fix pass over `website/dist/`. Classifies every issue into one of four buckets: **AUTO** (fixed silently — `lang`, viewport, `font-display: swap`, image dimensions, canonical URLs, `sitemap.xml`, `robots.txt`), **ONE_QUESTION** (asks once, e.g. base URL, then fixes), **DIALOG** (walks you through schema markup, alt text, titles, descriptions), **EXTERNAL** (exact manual steps, e.g. Google Search Console). Also has an image-optimization mode: WebP conversion, correct sizing per `design.md`, `<picture>` fallback wrapping. Run once after the first build, then again after major content changes.

## `/b2:illustrate` — Illustration

First run only: a style-brief interview, producing `docs/product/illustration-style.md`. Every run after that: generates image prompts, offers either the Gemini API or an external tool, reads back and evaluates whatever image you provide, and iterates until approved. Doesn't produce image files directly unless the API path is used. Offers background removal via `rembg` for spot illustrations and icons (not heroes).

Accepts an optional argument — a page name, path, or description, e.g. `/b2:illustrate about.md`. On a returning session, this skips the open "what needs illustrating today" question and goes straight to proposing prompts for that page. Without an argument, it asks first.

## `/b2:image` — Direct Image Generation

Explicit-invocation only — never triggered by a general "make an illustration" request; that's `/b2:illustrate`. Generates one image directly via the Gemini API. Requires a paid `GEMINI_API_KEY` in `.env` at the project root.

**Produces:** `website/src/images/*.png` (or a path you specify).

## `/b2:present` — Presentation Content

Not tied to the website build — works for any topic, any time. Mode-detects create vs. edit. On a
new topic: silently harvests context from any b2 docs and notes present, then a Socratic strategic
interview (the one idea, audience, enemy, proof, hook, and structure), then an outline you approve,
then the full reveal.js-flavored markdown. On an existing deck: surgical content edits only, no
re-interview. Offers to dispatch `/b2:present-design` (no theme yet) or `/b2:present-build`
(content ready).

**Produces:** `docs/presentations/{slug}/{slug}.md`.

## `/b2:present-design` — Presentation Theme

Run once per presentation theme, not once per presentation — grounds in your website's locked
design language rather than starting fresh. Interview (stage context, motion intensity, audience) →
2-3 direction proposals → mockup concepts on a fixed 6-slide sample set, reviewed in a gallery →
iterate → lock.

**Produces:** `website/presentation-themes/{name}/`, `website/presentation-mockups/`.

## `/b2:present-build` — Presentation Render

Applies a locked theme to a deck's markdown, producing (or surgically updating) its live HTML.
Standalone and per-deck — run it whenever you want that specific presentation rendered or updated,
never automatically. Preserves the hand-crafted design of any slide you didn't just edit.

For the full mechanics — theme resolution, slide-id reconcile, shared runtime, limitations — see
[presentations.md](presentations.md).

**Produces:** `website/dist/presentations/{slug}/index.html`, published with the site.

---

## Direct Build Commands (when a Makefile is in use)

`/b2:build` is the recommended entry point, but if `/b2:setup` detected a `website/Makefile`, these work directly from `website/`:

```bash
make              # Build dist/ — aborts if stale .md files detected
make watch        # Watch mode — warns (doesn't abort) on stale .md, rebuilds on .html/.css/.js changes
make clean        # Remove dist/
make publish      # Build + FTP dist/ to host via websync.cfg
```

`make watch` requires `fswatch` (`brew install fswatch`). None of this is required — if no Makefile exists, `/b2:setup` falls back to the plugin's bundled assembly scripts and `/b2:build` drives those instead.
