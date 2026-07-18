# Site Import Trigger (shared gate)

Invoked identically by `talk-expert`, `write-expert` (first run only, from `create.md`), and
`structure-expert`. Asks the "existing site?" question at most once per project.

## Step 1 — Check the marker

Read `website/docs/decisions.md` (Read tool; tolerate FileNotFoundError — treat as "not asked").

If it contains a `## Site Import` section: already asked. Skip this entire gate silently and proceed
to the skill's normal flow. Do not mention this step to the user.

## Step 2 — Check freshness

If no marker yet, check whether the project looks fresh:

```bash
test -f docs/product/vision.md && ls website/src/*.md >/dev/null 2>&1 && echo "established" || echo "fresh"
```

If `established` (both vision.md exists AND website/src/*.md files exist): skip the gate silently —
don't retroactively offer an import on a project that's already past bootstrap. Proceed to the
skill's normal flow.

If `fresh`: continue to Step 3.

## Step 3 — Ask

> "Is there an existing site we should use as a starting point — for content, structure, design, or
> assets? (or 'no' to start fresh)"

## Step 4 — Handle the answer

**If no (or declines):** record the marker (Step 5) with result `declined`, then continue this
skill's normal flow unchanged.

**If yes:**
1. State the scope guard: "I'll only import from a site you own or have rights to reuse — confirm
   that's the case here." Wait for confirmation.
2. Ask which capabilities apply: "Content (page text), Structure (page map/nav), Design (look and
   feel), Assets (logo/images) — which of these, and what's the URL?" Default to all four if the
   user just gives a URL without specifying.
3. Ask for the site's base URL if not already given.
4. For each selected capability, read and follow the matching file in this module:
   `content.md`, `structure.md`, `design.md`, `assets.md` (all in `${CLAUDE_PLUGIN_ROOT}/shared/site-import/`).
5. Record the marker (Step 5) with result `imported` and the list of capabilities run.
6. Continue this skill's normal flow — now seeded with whatever was imported (e.g. structure-expert's
   interview references `website/docs/site-import/pages.md` if Structure ran).

## Step 5 — Record the marker

Append to `website/docs/decisions.md` (Read tool first if it exists, to append rather than
overwrite; create the file with just this section if it doesn't exist yet — Write tool):

Declined:
```markdown
## Site Import
*Checked: YYYY-MM-DD*

- Asked: yes
- Result: declined
```

Imported:
```markdown
## Site Import
*Checked: YYYY-MM-DD*

- Asked: yes
- Result: imported
- Source: https://example.com
- Capabilities: content, design
```

This section is the marker itself — its presence is what Step 1 checks for. Never write it twice;
if somehow both a decline and an import happen across a broken session, the later write replaces the
section rather than duplicating it.
