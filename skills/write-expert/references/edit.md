# Edit Workflow

Use this workflow when updating or maintaining existing content.

---

## Step 1 - Locate the File

If the user named a file or page, resolve the path:
- Named a slug or page title → check `website/src/{slug}.md` and `website/src/**/{slug}.md`
- Named a file path → read it directly

If the file cannot be found, tell the user and ask them to confirm the path.

Read the file before proceeding.

---

## Step 2 - Understand the Edit

Ask what needs to change if it isn't clear from the request. Useful questions:

- "What's wrong with the current version?" (outdated info, wrong tone, missing section, too long?)
- "Is this a content change, a voice/tone change, or both?"
- "Is there anything in the current version that should be kept as-is?"

Do not ask all of these - ask only what the request leaves unclear. If the request is specific ("rewrite the opening paragraph to be less corporate"), proceed without interrogating.

Before proposing changes, do a quick placement check: does the requested content match this page's Job in `content-types.md`? If `content-types.md` has no Job lines, use the sibling pages' frontmatter `description` + opening paragraph instead (quick read, not full bodies) - and check `docs/product/vision.md` too, if it exists, since it can already cover ground a page edit might restate. If the new/changed content reads as another page's job - or restates something `vision.md` already establishes - say so before writing: name the page (or doc) that owns it and suggest linking to it or cutting the overlap, rather than silently proceeding. This applies whether or not the user framed the request as "these feel repetitive" - check every structural/message-level edit, not just ones flagged as overlapping. (Pure copy-fixes - typos, tone tweaks, a factual correction - don't need this check.)

If two pages already feel repetitive, don't default to trimming one of them - check (or set) each page's Job in `content-types.md` (see structure-expert) and give them genuinely different angles or forms, not just different lengths. A shorter version of the same point is still the same point.

---

## Step 3 - Propose the Changes

Before rewriting, show what will change. Format as a brief before/after or a summary of edits:

**For targeted edits (single section, paragraph, or headline):**

Show the proposed replacement inline:

> **Current:**
> "We are a team of passionate professionals dedicated to excellence."
>
> **Proposed:**
> "We fix tax problems. Fast, without jargon, without surprises."
>
> Want me to apply this, or adjust the direction first?

**For broader rewrites (whole page or major restructure):**

Summarise the planned approach rather than showing the full rewrite:

> "I'll keep the three-section structure but rewrite the opening to lead with the problem you solve, tighten the middle section by cutting the generic benefits list, and sharpen the CTA. The frontmatter stays as-is. Want me to proceed?"

Wait for approval before writing. Do not rewrite the file speculatively.

---

## Step 4 - Write the Updated File

Apply the approved changes. Rules:

- **Preserve frontmatter** unless the edit explicitly targets it (title change, date update, etc.)
- **Preserve structure** unless the user or proposal called for restructuring
- **Do not touch sections** the user didn't ask about - surgical edits only
- Match voice and tone to `website/docs/decisions.md` as loaded in context

Write the full file back (not a partial patch).

---

## Writing Standards

**Voice:** Match the tone from `website/docs/decisions.md`. If tone adjectives are "warm, direct, specific" - every sentence should pass that test.

**Headlines:** Make a specific claim. Something only this site can say.

**Openings:** No "Welcome to..." or "We are..." - start with the thing that matters.

**CTAs:** Use the primary CTA from `website/docs/decisions.md` unless explicitly changing it.

**Excluded topics:** Respect the "What we don't say" list in `website/docs/decisions.md` if it exists.

**Self-reference check:** Any sentence referring to "this site," "this page," or the project itself - read it from the actual position of someone currently on that page. A page can't tell its reader to go verify something they're already looking at. Claims about how the site "works" or "breaks" must be technically accurate for its actual deployment model - e.g. a static build is inert once published, so don't imply a build-time tool stays coupled to it at runtime.

---

## After Editing

Tell the user: "Updated `website/src/{path}.md`."

If the change is significant (full rewrite, new section), ask:
"Shall I run /b2:build to rebuild and preview? (yes/no)"

If yes: use the Skill tool to invoke `b2:build-expert`. Once it completes, run the **Automatic Design Self-Check** (see `SKILL.md`) - it classifies the resulting partial diff as structural or copy-only and, for structural edits to a page that already existed in `website/dist/`, delegates to `website-review-expert` for that one page before you give the final report.
If no: "Run /b2:build when you're ready to preview."

`website/docs/status.md` normally doesn't need touching for edits - that file tracks setup phase completion, not content revisions. Exception: if `website/docs/status.md` exists and has no `- [x] Write` line yet, add it now (`- [x] Write     → website/src/`, preserving all other lines exactly) - editing an existing page proves content already exists, so the Write phase is functionally done even if it was never marked. If a `- [x] Write` line is already present, leave the file untouched.
