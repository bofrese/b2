---
name: b2
description: This skill should be used when the user runs "/b2", asks "what should I do next", "where am I in the b2 setup", "show b2 status", "what is b2", "how does it work", or wants to know which b2 command to run. Detects project state from file existence and recommends exactly one next action. In maintenance mode, dispatches to other skills on request.
---

# b2

**Guide mode:** If the user asks "what is b2", "how does b2 work", or a similar explanatory question - read `${CLAUDE_PLUGIN_ROOT}/skills/b2/resources/knowledge.md` using the Read tool and answer from that document.

**Status mode (default):** Detect the current b2 project state from file existence and output a compact status table. Then show what's available now with a one-liner each, marking one as recommended (→). Add `/b2:talk` as an anytime option in all setup states. Still opinionated - not a neutral menu.

**Dispatch mode (maintenance only):** If the user says "run build", "start the server", "build the site", etc. - invoke the corresponding skill directly using the Skill tool rather than asking them to run a command themselves.

---

## State Detection

Run this once via Bash, from the project root:

```
sh "${CLAUDE_PLUGIN_ROOT}/skills/b2/scripts/status.sh"
```

It prints `KEY=value` lines covering every check below in one pass - do not use Read for these files individually, the script replaces all of it:

| Key | Phase | Meaning |
|-----|-------|---------|
| `VISION` | Vision | `docs/product/vision.md` exists |
| `BRAND` | Brand | `docs/product/website-design-brief.md` or `docs/product/design-brief.md` exists |
| `STRUCTURE` | Structure | `website/docs/content-types.md` exists |
| `WRITE` | Write | `website/docs/status.md` contains `- [x] Write` |
| `DESIGN` | Design | `website/theme/{THEME}/components.md` exists |
| `SYNC` | Sync | `website/docs/status.md` contains `- [x] Sync` |
| `SETUP` | Setup | `website/b2.cfg` contains `BUILD_TOOL=` |
| `THEME` | - | value of `THEME=` from `website/b2.cfg`, default `b2` |
| `IN_PROGRESS` | - | first line containing `IN PROGRESS` in `website/docs/status.md`, or `none` |

---

## Output Format

Output exactly two sections:

**1. Status table** (compact, always shown):

```
## B2 Setup Status

| Phase     | Status |
|-----------|--------|
| Vision    | ✓ complete |
| Brand     | ✓ complete |
| Structure | ✗ pending  |
| Write     | ✗ pending  |
| Design    | ✗ pending  |
| Sync      | ✗ pending  |
| Setup     | ✗ pending  |
```

**2. What's available now** - the recommended action marked with →, plus `/b2:talk` as an always-present anytime option. Other alternatives shown only when there's a genuine reason to skip ahead.

---

## Routing Logic

Apply in order - use the first rule that matches:

1. **In-progress detected** (`website/docs/status.md` has an `IN PROGRESS` entry AND the phase's output file does not yet exist):
   For example: design `IN PROGRESS` but `website/theme/{THEME}/components.md` does not exist → resume.
   If the output file already exists, the IN PROGRESS entry is stale - ignore it and apply subsequent rules.
   Output: `[Phase] is in progress - resume with /b2:[phase]`

2. **Nothing set up** (no vision.md):

   ```
   ## Where to start

   → /b2:vision ← structured interview, ~10 minutes, creates your vision document
      /b2:talk - explore ideas more broadly first, no structure required
   ```

3. **Vision only** (vision.md exists, no website-design-brief.md and no design-brief.md):

   ```
   ## What you can do now

   → /b2:brand ← recommended next - turn your vision into positioning and voice
      /b2:talk - explore ideas, refine messaging, or capture notes (anytime)
   ```

4. **Brand done, no structure** (website-design-brief.md or design-brief.md exists, no content-types.md):

   ```
   ## What you can do now

   → /b2:structure ← recommended next - map out your site pages and content types
      /b2:talk - explore ideas, refine messaging, or capture notes (anytime)
   ```

5. **Structure done, write not started** (content-types.md exists, no `[x] Write` in website/docs/status.md):

   ```
   ## What you can do now

   → /b2:write ← recommended next - real content makes your design mockups significantly better
      /b2:talk - explore ideas, refine messaging, or capture notes (anytime)
      /b2:design - skip ahead to design (mockups will use stub content)
   ```

6. **Write done, no design** (`[x] Write` in website/docs/status.md, no components.md):

   ```
   ## What you can do now

   → /b2:design ← recommended next - mockups, theme selection, and CSS generation
      /b2:talk - explore ideas, refine messaging, or capture notes (anytime)
      /b2:write - write more content pages first
   ```

7. **Design done, sync not done** (components.md exists, no `[x] Sync` in website/docs/status.md):

   ```
   ## What you can do now

   → /b2:sync ← recommended next - convert your .md files to HTML before building
      /b2:talk - explore ideas, refine messaging, or capture notes (anytime)
   ```

8. **Sync done, no setup** (`[x] Sync` in website/docs/status.md, `b2.cfg` missing or has no `BUILD_TOOL=` line):

   ```
   ## What you can do now

   → /b2:setup ← recommended next - configure build environment and run first build
      /b2:talk - explore ideas, refine messaging, or capture notes (anytime)
   ```

9. **All setup complete** (`b2.cfg` contains `BUILD_TOOL=`):
   Show maintenance options - see Maintenance Mode below.

---

## Maintenance Mode

When all phases are complete, show:

```
## B2 Setup Status

| Phase     | Status     |
|-----------|------------|
| Vision    | ✓ complete |
| Brand     | ✓ complete |
| Structure | ✓ complete |
| Write     | ✓ complete |
| Design    | ✓ complete |
| Sync      | ✓ complete |
| Setup     | ✓ complete |

## Your site is ready. What do you want to do?

- `/b2:write` - write or update a content page
- `/b2:build` - detect stale files, sync, assemble, and verify
- `/b2:sync` - convert changed .md files to HTML (explicit)
- `/b2:serve` - start local server on dist/
- `/b2:website-review` - screenshot and evaluate a page visually
- `/b2:talk` - explore ideas, refine messaging, or capture notes (anytime)
- `make publish` - publish to your host (requires websync or rsync configured in Makefile)

In dispatch mode, the user can say "run build", "start the server", etc. - invoke the corresponding skill directly.
```

In maintenance mode, offering multiple options is correct - the user is no longer in a linear setup flow.

---

## Tone and Length

- Direct and brief. No padding.
- No "Great news!" or "Let me help you with that."
- Status table first, recommendation second.
- Total output: under 25 lines in setup mode, under 35 lines in maintenance mode.
