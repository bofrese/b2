# Edit Workflow

Use this workflow when updating an existing presentation. No re-interview - the spine (big idea,
audience, enemy, proof, hook, arc) was already built once in create mode; edit mode only touches
content.

---

## Step 1 - Locate the Deck

If the user named a slug or title, resolve the path:
- Named a slug → check `docs/presentations/{slug}/{slug}.md`
- Named a title or topic → search `docs/presentations/*/` for a matching slug or an `H1` matching the title

If the deck cannot be found, tell the user and ask them to confirm the slug.

Read the file before proceeding.

---

## Step 2 - Understand the Edit

Ask what needs to change if it isn't clear from the request:

- "Which slide(s), and what's wrong with them?"
- "Content change, reorder, cut, or a new slide?"

Do not ask all of these - ask only what the request leaves unclear. If the request is specific ("rewrite slide 4 to lead with the client story instead of the stat"), proceed without interrogating.

---

## Step 3 - Propose the Changes

Before rewriting, show what will change:

**For a single-slide edit:**

> **Current (slide "the-enemy"):**
> "..."
>
> **Proposed:**
> "..."
>
> Want me to apply this, or adjust the direction first?

**For structural changes (reorder, add, cut):**

> "I'll move 'the-proof' before 'the-hook' and cut 'background' entirely - three slides become two. Want me to proceed?"

Wait for approval before writing. Do not rewrite the file speculatively.

---

## Step 4 - Write the Updated File

Apply the approved changes. Rules:

- **Preserve `<!-- .slide: id="..." -->` directives on untouched or content-edited slides exactly
  as they are.** Never invent, remove, or renumber an id yourself - id lifecycle belongs entirely
  to `present-build-expert`'s backfill/reconcile pass, which runs at build time, not here. A newly
  added slide simply has no id comment yet; that's expected, the next build assigns one.
- **Preserve frontmatter** (`theme:`, `transition:`, etc.) unless the edit explicitly targets it.
- **Do not touch slides** the user didn't ask about - surgical edits only.
- Read `references/slide-format.md` now and follow it for any new or rewritten slide content
  (titles as active claims, max 3 bullets, specific visual comments, substantial presenter notes).

Write the full file back (not a partial patch).

---

## After Editing

Tell the user: "Updated `docs/presentations/{slug}/{slug}.md`."

Then offer to render:

> "Ready to update the live deck? I can run `/b2:present-build {slug}` now - it'll only touch the slides that actually changed. (yes/no)"

- Yes → use the Skill tool to invoke `present-build-expert`, passing `{slug}`.
- No → "Run `/b2:present-build {slug}` when you're ready."

If the deck's `theme:` frontmatter is still unset (no `/b2:present-design` has run yet), mention it
instead of offering build: "This deck has no presentation theme yet - run `/b2:present-design`
first, then `/b2:present-build {slug}`."
