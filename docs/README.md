# b2 Plugin Documentation
*Last verified: 2026-07-16*

b2 is a Claude Code plugin that takes a static website from blank folder to published site — vision, brand, content, design, build, and SEO, all as guided AI workflows.

This folder documents the plugin itself (what you install). It ships inside the plugin, so it travels with every install.

## Start Here

| If you want to... | Read |
|---|---|
| Install b2 and run your first command | [getting-started.md](getting-started.md) |
| Look up what a specific command does | [commands.md](commands.md) |
| Know what files b2 creates in your project, and where | [files-and-folders.md](files-and-folders.md) |

## The Short Version

```
/b2:vision → /b2:brand → /b2:structure → /b2:write → /b2:design → /b2:sync → /b2:setup
```

Then day-to-day: `/b2:write` → `/b2:build` → `/b2:serve` → `/b2:website-review`

Run `/b2` any time — it detects what's done in your project and tells you the one next command to run. It is the intended entry point; you should rarely need to consult the phase order above directly.

## Scope Note

This documents the b2 **plugin** — its commands, skills, and conventions. It does not document any specific website built with b2. A project built with b2 gets its own `website/CLAUDE.md`, written by `/b2:setup`, documenting that project's file structure and build conventions.
