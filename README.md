# b2

AI-powered static website builder. From blank folder to published site.

B2 guides a site owner through design and content decisions via structured interviews, generates mockup alternatives, and produces a consistent visual theme and maintained site from plain markdown files.

See [the B2 website](https://b2.bofrese.dk) for details on how it works, or read [the docs](docs/README.md).

## Setup Flow (run once, in order)

| Step | Command | Creates |
|------|---------|---------|
| 1 | `/b2:vision` | `docs/product/vision.md` |
| 2 | `/b2:brand` | `docs/product/website-design-brief.md`, `website/docs/decisions.md` |
| 3 | `/b2:structure` | `website/docs/content-types.md`, stub pages |
| 4 | `/b2:write` | `website/src/*.md` - real copy for mockups |
| 5 | `/b2:design` | `website/mockups/`, `website/theme/{THEME}/` |
| 6 | `/b2:sync` | `website/partials/*.html` - HTML fragments |
| 7 | `/b2:setup` | `website/b2.cfg`, platform detection, first build |

Run `/b2` at any time to see your current status and what to do next.

## Day-to-Day Commands

```
/b2:write           Write or update a content page (harvests existing content first)
/b2:build           Detect stale files, sync, assemble dist/, flag pages for review
/b2:sync            Convert changed .md files to HTML partials (explicit)
/b2:serve           Start a local server on dist/ and report the URL
/b2:website-review  Screenshot and visually evaluate a page against the design system
make                Assemble dist/ directly (macOS/Linux, requires make)
make publish        Publish to your host
```

## Prerequisites

- Claude Code
- `website/` with a Makefile (see `website/Makefile`) - optional; `make` is detected at runtime and `/b2:build` uses built-in scripts if unavailable
- Playwright (optional) - for `/b2:website-review` visual verification

## Bob Compatibility

B2 uses the same file locations as Bob (`docs/product/vision.md`, `docs/product/website-design-brief.md`). Bob users get continuity across both plugins. Bob is not required.
