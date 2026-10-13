---
name: write-expert
description: This skill should be used when the user runs "/b2:write", asks to "write a page", "write a post", "create content", "write the about page", "draft a blog post", "write copy for", "edit a page", "update the about page", "revise the copy", "rewrite the homepage", "improve the text on", or "change the content of". Handles both creating new content and editing existing content using brand voice from website/docs/decisions.md.
---

# b2 Write Expert

Write in the site owner's voice, as the files below describe it, not in a generic copywriter voice. Apply the `plain-writing` skill in the personal-voice register: it removes AI slop, and these files are the project voice guide. Write for the specific audience in the vision, not for a generic visitor. Cut copy that does not help that reader decide or act.

---

## Load Context

Read these files if they exist. Adapt to what's available - do not halt if files are missing:

1. `docs/product/vision.md` - purpose and audience
2. `docs/product/website-design-brief.md` - tone of voice, key messages, what not to say (fall back to `docs/product/design-brief.md` if missing)
3. `website/docs/content-types.md` - page type conventions, frontmatter specs, and per-page "Job" lines (what each page owns, what it must not repeat - used for the overlap check in create.md/edit.md)
4. `website/docs/decisions.md` - brand voice synthesis (most compact, use this for tone)
5. `docs/notes/README.md` - knowledge base index (optional). If it exists, scan for files relevant to the current writing task and read them.

If none of these exist, write plain, natural prose and suggest `/b2:brand` to define the voice.

---

## Detect Mode

Before proceeding, determine which mode applies:

**Edit mode** - the user references an existing file, page, or piece of copy they want changed. Signals: "edit", "update", "revise", "rewrite", "improve", "change", "fix the copy on", or they name a file that already exists in `website/src/`.

**Create mode** - the user wants new content that does not yet exist. Signals: "write", "draft", "create", "add a page", or they describe a page that doesn't exist yet.

If ambiguous: check whether `website/src/{likely-slug}.md` exists. If it does, default to edit mode and confirm: "Found an existing file - I'll edit that. Is that right, or do you want to start fresh?"

---

## Workflow

Load the reference for the detected mode and follow it:

- **Create mode** → read `references/create.md` and follow it
- **Edit mode** → read `references/edit.md` and follow it

---

## Automatic Design Self-Check (after build)

Shared logic, invoked from both `create.md` and `edit.md` after `/b2:build` runs. This is a **separate** check from the site-structure/message overlap check in Step 2b (create.md) / Step 2 (edit.md) - that one catches content/message duplication between pages; this one catches visual/structural design-quality regressions on the single page just edited. Run both where applicable; neither replaces the other.

**Scope guard - skip entirely when:**
- `website/dist/{page}.html` did not exist before this edit (brand-new page, still in initial `/b2:design`/first-build phase - no prior design to regress against).
- The edit was copy-only (see classification below).

**Classify structural vs. copy-only:** compare `website/partials/{page}.html` before the sync/build to after (`git diff` on the partial, since `/b2:sync` regenerates it from the edited `.md`).
- **Copy-only** - only text nodes inside existing tags changed. No self-check.
- **Structural** - any of: a section added/removed, a class/component introduced that wasn't already used on this page, section order/nesting changed, a new image slot added. Triggers the self-check below.

**Self-check flow (structural edits only):**
1. Use the Skill tool to invoke `website-review-expert`, scoped to just this one page (equivalent to `/b2:website-review {page}`). Do not reimplement its Step 4 criteria or Step 4b art-direction pass here - delegate.
2. Mechanical fixes (that skill's Step 5 - layout/SEO/component compliance) apply automatically, same as when a user runs it directly.
3. Design Proposals (Step 4b output - reskins, new components, illustration opportunities) are **not** applied automatically. Carry them into write-expert's final report for user confirmation, same rule website-review-expert follows for itself.
4. Report using website-review-expert's Step 6 Fixed/Flagged format, appended after write-expert's normal completion message, and close with: "I made these design-relevant changes - what do you think?"

If website-review-expert halts (no local server, Playwright unavailable), surface that halt message rather than silently skipping the self-check.
