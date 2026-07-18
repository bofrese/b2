---
name: build-expert
description: This skill should be used when the user runs "/b2:build", asks to "build the site", "rebuild", "assemble the pages", or "update dist/". Orchestrates the full build pipeline: stale detection, sync, assembly, and optional visual verification.
---

# b2 Build Expert

Day-to-day build orchestrator. Detect stale files → sync if needed → assemble → optionally verify. Does not reimplement make — calls it when available.

---

## Prerequisite Check

Read `website/b2.cfg` if it exists to determine `BUILD_TOOL`. If missing, default to `BUILD_TOOL=make` on macOS/Linux or detect:

```bash
which make 2>/dev/null && echo "make" || echo "scripts"
```

---

## Step 1 — Check for Stale Files

Run stale detection using the plugin script (Bash tool):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/build-expert/scripts/check-stale.sh"
```

Parse the output by prefix:
- `item:` lines — content files needing sync
- `index:` lines — index files needing regeneration
- `theme:` lines — theme CSS/JS files newer than their `dist/` copies

Report:
- `"N content file(s) stale."` / `"Nothing to sync."` (for item: + index:)
- `"Theme files changed — will copy to dist/ on assembly."` (for theme: lines)

---

## Step 2 — Sync if Stale

If `item:` or `index:` lines were found, use the Skill tool to invoke the `b2:sync-expert` skill — it will re-detect and convert all stale files. Do not call `/b2:sync` recursively — invoke the skill directly.

After sync completes, report what was converted.

---

## Step 3 — Assemble

**If BUILD_TOOL=make:**

```bash
cd website && make
```

Report success or failure. On failure: show error, diagnose, suggest fix. Do NOT auto-fix.

**If BUILD_TOOL=scripts:**

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/build-expert/scripts/assemble.sh"
```

Report result.

---

## Step 4 — Verify (Optional)

For any **newly created** partial (first sync of a file), offer visual verification:

> "New page detected: `{page}`. Run `/b2:website-review {page}` to screenshot and verify the layout."

Do not auto-run website-review on every build — only flag new or significantly changed pages (a partial growing by >50% in size or going from stub to real content).

If Playwright is not installed (determined by attempting `browser_take_screenshot` or running `npx playwright --version 2>/dev/null`), note:
> "Playwright not found — skipping visual verification. Run `/b2:website-review` manually after `/b2:serve`."

---

## Step 5 — Report

```
Build complete.

  Synced:  2 files
  Built:   5 pages → website/dist/

  about.html          ✓ new — run /b2:website-review about.html to verify
  posts/index.html    ✓ updated

Run /b2:serve to preview.
```

If nothing was stale and make succeeded:

```
Build complete. Nothing to sync. 5 pages assembled → website/dist/
```
