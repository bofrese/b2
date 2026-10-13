# Getting Started
*Last verified: 2026-07-16*

## Install

In Claude Code:

```
/plugin marketplace add bofrese/claude-plugins
/plugin install b2@bofrese-plugins
```

**Requirements:** Claude Code. A Claude Pro plan is recommended - b2 runs long, multi-step AI workflows, and free-tier rate limits can interrupt them mid-phase.

## First Run

Run `/b2` in the root of the project where you want the site to live. It reads project state from the filesystem and recommends exactly one next action - it never presents a menu during setup.

```
/b2
```

First time, it recommends `/b2:vision`. Follow its recommendation each time you run it; it re-detects state after every command.

You don't need a blank folder. b2 works equally well:

- **Starting fresh** - a new, empty repo for the site alone.
- **Alongside an existing product repo** - run `/b2` at the root of your existing codebase to add a marketing/docs site in the same repository. b2 only touches the folders listed below; it won't reorganize or interfere with the rest of your code.

### What Gets Created or Reused

b2 creates `docs/` at the project root (for vision and brief docs), and does almost everything else under `website/` - content, theme, status/decisions docs, and the built site all live there, self-contained. If any of these already exist from a prior b2 run, it reads and extends them rather than overwriting. Full breakdown, including what's safe to hand-edit: [files-and-folders.md](files-and-folders.md).

## The Setup Flow

b2 enforces this order the first time through a project - running a later command before its prerequisite exists stops with a clear error rather than guessing:

```
/b2:vision → /b2:brand → /b2:structure → /b2:write → /b2:design → /b2:sync → /b2:setup
```

| Step | What happens |
|---|---|
| `/b2:vision` | Interview: purpose, audience, success criteria. Produces `docs/product/vision.md`. |
| `/b2:brand` | Interview: name, tagline, positioning, tone of voice, primary CTA. Produces `docs/product/website-design-brief.md` and `website/docs/decisions.md`. |
| `/b2:structure` | Site map: pages, content types, navigation. Produces `website/docs/content-types.md` and stub content files. |
| `/b2:write` | Writes real copy into the stub pages, in your brand voice. |
| `/b2:design` | Interview → mockups → theme. Produces `website/theme/{name}/` - the CSS, components, header/footer, and scripts. |
| `/b2:sync` | Converts your `.md` content into semantic HTML using the theme's component vocabulary. |
| `/b2:setup` | Detects your build tool, asks about hosting path, writes `website/b2.cfg`, runs the first build. |

Optionally, run `/b2:talk` before or during any of this - it's a no-structure exploration mode that captures notes future commands read automatically, so the less you have figured out, the more useful it is to run first.

## Day-to-Day Workflow

Once setup is complete, `/b2` switches to maintenance mode and stops recommending a single next step - you drive it:

```
Edit website/src/page.md
→ /b2:build          detects stale files, syncs, assembles dist/
→ /b2:serve          local server at http://localhost:8099
→ /b2:website-review requires the server running - visual QA pass
→ /b2:seo            audit and fix, run after major content changes
```

Writing a new page:

```
/b2:write [topic]   outline → your approval → writes markdown
/b2:build           sync + assemble
/b2:serve           preview
```

## Publishing

`website/dist/` is the deployable output - push it to GitHub Pages or Netlify directly, or drag it into any static host. If a Makefile is in use (see [files-and-folders.md](files-and-folders.md)), `make publish` will FTP `dist/` to a host configured in `websync.cfg`.

## FAQ

**Does b2 work with an existing site?** Adding b2 to an existing product repo (to add a site alongside your app code) works fine - see [First Run](#first-run). What's *not* the tested path is pointing b2 at a site that already has content and a design of its own and asking it to take over - it's built to create a site through its own phases, not import one.

**Can I edit the theme manually?** Yes - `website/theme/{name}/` is yours. Keep `styles.css` and `components.md` in sync: `/b2:sync` only uses classes listed in `components.md`, so a class defined in one but not the other silently can't be used.

**AI output isn't what I wanted - now what?** Edit the source markdown in `website/src/` and re-run `/b2:build`. `/b2:sync` integrates changes surgically into the existing HTML partial rather than regenerating it from scratch.

**Where does it get hosted?** Anywhere. `dist/` is a plain static site folder.
