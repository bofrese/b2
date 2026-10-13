# Create Workflow

Use this workflow when writing new content that does not yet exist.

---

## Step 0 - Site Import Check (first run only)

Read `${CLAUDE_PLUGIN_ROOT}/shared/site-import/trigger.md` and follow it before Step 1. It checks a
project-wide marker and a freshness condition (no `docs/product/vision.md`, or no
`website/src/*.md` files yet) itself - on a returning project, or one already asked by
`talk-expert`/`structure-expert`, it silently no-ops and you proceed straight to Step 1. If it runs
the Content capability, the pages it writes satisfy this create request (or a sibling page) directly
 - no need to also run Step 1's harvest question for a page it already produced.

## Step 1 - Content Harvest (Before Interviewing)

Before asking any questions, check whether the user has existing material to start from.

Ask:

> "Do you have existing content to work from? An old website URL, a document, a deck, a press release, or any text you've used before? Starting from real material produces much better copy than starting from scratch. (If not, that's fine - we'll do an interview.)"

**If yes - harvest:**

- **URL:** Fetch it using the WebFetch tool. Extract usable copy by section (headlines, body paragraphs, CTAs). Ignore nav, footers, cookie banners.
- **Pasted text or file path:** Read/parse it directly.

After extracting, show the user what was found:

> "Found content for: **About** (good), **Services** (partial - missing pricing), **Contact** (nothing useful). I'll use this as the base and only ask about the gaps."

Proceed to interview only for sections with no usable content. Mark sections that couldn't be harvested as placeholders in `website/docs/status.md` (see After Writing section).

**If no - proceed with interview:**

If the user has no existing material, proceed directly to Step 2. No interview needed.

**If URL fetch fails** (site down, network error, auth wall): tell the user, and fall back to the interview flow.

---

## Step 2 - Understand the Request

If the user's message does not describe what to write, ask: "What do you want to write?"

From their description, determine:
1. **Content type:** match against `content-types.md` types by purpose. If no content-types.md exists, default to `page`.
2. **File path:** root pages → `website/src/{slug}.md`; typed content → `website/src/{type}/{slug}.md`
3. **Slug:** derive from title (lowercase, hyphens, no special characters)

If the type is ambiguous, confirm before proceeding: "This sounds like a post - I'll write it to `website/src/posts/your-title.md`. Is that right?"

---

## Step 2b - Check for Overlap With Sibling Pages

If `content-types.md` has "Job" lines, read them before outlining. If this page's likely content would repeat another page's Job, don't write a shorter version of that page's content - either cut the overlapping part and link to the page that owns it, or find a genuinely different angle or form for it. A trimmed restatement of the same point is still the same point; the fix is a different job, not fewer words. **Say this in the outline proposal** (Step 3), don't just self-correct silently - e.g. "Heads up: the workflow detail belongs to how-it-works.md's job, so I've linked to it instead of repeating it here."

If `content-types.md` has no Job lines yet (older project, or skipped as low-risk), derive purpose summaries on the fly instead of skipping the check: read each `website/src/*.md` file's frontmatter `description` plus its opening paragraph (title + first sentence - not the full body) and compare against those. This is a quick read, not a full-site audit. Also check `docs/product/vision.md` if it exists - planned content that duplicates a section already established there (not just a sibling page) is still overlap.

If `website/src/` has no other pages yet (first page being written), skip this check - there's nothing to overlap with.

## Step 3 - Propose an Outline

Before writing any content, propose a structure for approval. Format:

```
Here's the outline I'd use for the {page title}:

1. **Opening** - [1-2 sentences]: What this is and who it's for. Concrete claim, not "welcome".
2. **Story / Context** - [2-3 paragraphs]: Why this exists. What problem it solves. What makes it different.
3. **What you get** - [bullet list]: 3-4 concrete things. Not benefits-speak - real specifics.
4. **CTA** - [1 sentence + button]: [Primary CTA from website/docs/decisions.md]

Does this structure work, or do you want to adjust it before I write?
```

Wait for approval or adjustments before writing. "Looks good", "go ahead", "yes" - proceed. Specific feedback - adjust outline and re-present.

---

## Step 4 - Write the File

On outline approval, write the markdown file to the correct path.

**Format:** Standard markdown with YAML frontmatter matching the content type's spec from `content-types.md`.

`title:` becomes the page's literal `<title>` tag at build time - write it as a real, specific search-result title (include the site/brand name), not a short internal label like "About" or "Docs".

If this page should never appear in search results (an internal demo, a duplicate, a mockup gallery), add `noindex: true` to the frontmatter.

**Example - page type:**
```markdown
---
title: "About Acme - Why We Built a Lightweight Alternative"
description: [1-sentence description for SEO and sharing]
---

[Content here - prose, headings, lists as needed]
```

**Example - post type:**
```markdown
---
title: Post Title
date: YYYY-MM-DD
tags: [tag1, tag2]
summary: One-sentence summary for the post listing.
---

[Post content here]
```

Use the correct frontmatter fields for the type. Do not add fields not in the spec.

If `content-types.md` is absent, use minimal frontmatter as fallback: `title` and `description` for pages; `title`, `date`, and `summary` for posts.

If `website/src/` does not exist, create it before writing (Bash: `mkdir -p website/src`).

---

## Writing Standards

**Voice:** Match the tone from `website/docs/decisions.md`. If tone adjectives are "warm, direct, specific" - every sentence should pass that test. Never default to generic marketing copy.

**Headlines:** Make a specific claim. "Tax prep without the stress" beats "Professional Tax Services". The right headline is something only this site can say.

**Openings:** No "Welcome to..." or "We are..." - these are throat-clearing. Start with the thing that matters.

**CTAs:** Use the primary CTA from `website/docs/decisions.md`. If not defined, ask: "What should a reader do next?"

**Length:** Match the type. Root pages: 200-600 words. Posts: as long as the content requires. Product pages: concise with scannable structure.

**Excluded topics:** Respect the "What we don't say" list in `website/docs/decisions.md` if it exists.

**Self-reference check:** Any sentence referring to "this site," "this page," or the project itself - read it from the actual position of someone currently on that page. A page can't tell its reader to go verify something they're already looking at. Claims about how the site "works" or "breaks" must be technically accurate for its actual deployment model - e.g. a static build is inert once published, so don't imply a build-time tool stays coupled to it at runtime.

---

## After Writing

Update `website/docs/status.md` to mark Write complete. Write-expert may run multiple times - update the Write line idempotently (do not reset other lines):

**If `website/docs/status.md` exists:** Read it. Set the Write line to `- [x] Write     → website/src/`. Preserve all other lines exactly. Write the entire file back.

**If `website/docs/status.md` does not exist:** Write the full block:

```markdown
# B2 Status
*Last updated: YYYY-MM-DD*

## Setup
- [ ] Vision    → docs/product/vision.md
- [ ] Brand     → pending
- [ ] Structure → pending
- [x] Write     → website/src/
- [ ] Design    → pending
- [ ] Sync      → pending
- [ ] Setup     → pending
```

Tell the user: "Written to `website/src/{path}.md`."

Then ask: "Shall I run /b2:build now to sync and assemble dist/? (yes/no)"

If yes: use the Skill tool to invoke `b2:build-expert`. Once it completes, run the **Automatic Design Self-Check** (see `SKILL.md`) - in practice this almost always no-ops for brand-new pages (the scope guard skips pages that didn't exist in `website/dist/` before the edit), but run it anyway for consistency; it only fires for real when a create-mode run overwrites a page that already had a prior build.
If no: "Run /b2:build when you're ready to preview."
