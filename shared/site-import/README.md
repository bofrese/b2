# b2 Site Import

Shared, b2-internal module for bootstrapping a b2 project from an existing website - the user's own
site being migrated onto b2. Mirrors `b2/shared/design/`'s pattern (B2-001): a README plus reference
procedures, invoked by multiple skills, not a standalone command.

**Scope guard:** only ever import from a site the user confirms is theirs (or one they hold rights
to reuse). This is a migration aid for the user's own content, not a general-purpose site-cloning
tool. Every capability that touches user-facing output (content, assets) states this to the user
before acting; `trigger.md` states it once at the point of offering the import.

## Four independently-selectable capabilities

| Capability | Reference | Produces | Consumed by |
|------------|-----------|----------|-------------|
| Content | `content.md` | Draft `website/src/{slug}.md` per page | `write-expert` (as existing files to edit) |
| Structure | `structure.md` | `website/docs/site-import/pages.md` | `structure-expert`'s interview (seed, not auto-applied) |
| Design | `design.md` | `website/docs/site-import/design-brief.md` + screenshots | `design-expert`'s interview opening (seed) |
| Assets | `assets.md` | Downloaded files in `website/src/images/` | `write-expert`/`design-expert` (as available media) |

None of these bypass the downstream skill's normal interview - they seed it with real material
instead of a blank page, same relationship `write-expert/references/create.md`'s Step 1 content
harvest already has to Step 3's outline proposal.

## Trigger

`trigger.md` defines the single shared "existing site?" gate asked once per project by whichever of
`talk-expert`, `write-expert` (first run only), or `structure-expert` runs first. See that file for
the marker mechanism (recorded in `website/docs/decisions.md`) that stops the other two from asking
again.

## Consumers

| Skill | Uses | Trigger point? |
|-------|------|-----------------|
| `talk-expert` | `trigger.md` | Yes |
| `write-expert` | `trigger.md` (first run only), `content.md` | Yes |
| `structure-expert` | `trigger.md`, `structure.md` output as interview seed | Yes |
| `design-expert` | `design.md` output as interview-opening seed | No - consumes only, never asks the gate |

## Playwright

The Design capability reuses `website-review-expert`'s exact Playwright detection order
(`b2/skills/website-review-expert/SKILL.md` Step 3) rather than reimplementing it. See `design.md`.

## Notes on WebFetch vs Playwright

Content and Structure default to WebFetch - sufficient for static/server-rendered pages, which covers
most small marketing sites b2 targets. If a page's fetched text is near-empty (JS-rendered SPA
content), note it in the report and point at the Design capability's Playwright path as a manual
fallback rather than silently switching strategies - a working WebFetch-based import is the priority,
not a general headless-browser scraper.
