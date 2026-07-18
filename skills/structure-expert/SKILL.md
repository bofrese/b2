---
name: structure-expert
description: This skill should be used when the user runs "/b2:structure", asks to "map out the site", "define site structure", "set up content types", "plan what pages the site needs", or wants to create website/docs/content-types.md. Conducts a site map interview and produces content type definitions and stub pages.
---

# b2 Structure Expert

Adopt the persona of an information architect. The goal is a clear site map with defined content types — not an exhaustive content plan. Structure for clarity, not completeness. This output feeds directly into `/b2:design`, which reads `content-types.md` to build mockups with accurate navigation.

---

## Before Starting

Ensure required directories exist (Bash tool — run before any Write call):

```bash
mkdir -p website/docs website/src
```

---

## Prerequisite Check

Read `docs/product/vision.md`. Read `docs/product/website-design-brief.md` if it exists; otherwise try `docs/product/design-brief.md`. If neither exists, stop:

> "Run `/b2:brand` first — site structure should be grounded in brand positioning."

Use both documents throughout the interview to test alignment.

## Site Import Check (once per project)

Read `${CLAUDE_PLUGIN_ROOT}/shared/site-import/trigger.md` and follow it. It silently no-ops on a
returning project or one already asked (by `talk-expert` or `write-expert`); it only surfaces a
question on a fresh project.

Separately, and regardless of whether the trigger fired this session, check for
`website/docs/site-import/pages.md` (Read tool; tolerate FileNotFoundError). If present — from any
earlier Structure import, this session or a prior one — open the Interview Topics below by presenting
its Navigation/Root pages/Recurring types content back to the user for confirmation ("Here's what I
found on your existing site — does this match what you want here, or should we change it?") instead
of asking topic 1 and 2 from a blank page. Still ask topics 3-5 normally; the import only seeds the
page/type list, not navigation-order or user-journey questions.

## Notes Context (Optional)

Read `docs/notes/README.md` using the Read tool if it exists. Scan for categories
relevant to site structure and content (e.g., ideas.md, raw-material.md) and read
those files. Notes may contain page ideas or content types worth including.
If `docs/notes/` does not exist, skip silently.

---

## Interview Topics (ask in order, one at a time)

**1. Root-level pages**
"What pages does this site need at the top level? Think about: home, about, contact, services, portfolio, pricing, blog, FAQ. What does this site actually need?"

Guide toward a lean set. Most small sites need 4–6 root pages. More is not better.

**2. Recurring content types**
"Does this site have any content that repeats in the same format — like blog posts, case studies, products, services, team members, projects? What types recur?"

For each recurring type, ask: "What's the minimum information each one needs?" (frontmatter fields)

**3. Index pages**
For each recurring type: "Should there be a listing page where visitors can browse all of them? (e.g., /posts/ shows all posts)"

**4. Navigation**
"What goes in the site header navigation? List the items in the order they should appear."

This is what appears in every mockup. Keep it to 4–6 items. If they want more, push back: "Most sites keep navigation to the highest-priority items. Which 5 are essential?"

**5. Primary user journey**
"Walk me through the path from landing page to the most important action. What pages does a visitor visit?"

This informs which pages are entry points (get a hero section) and which are destination pages.

---

## Writing content-types.md

Write `website/docs/content-types.md` using the Write tool.

Use this format for each content type:

```markdown
## page
Path: src/*.md
Partials: partials/*.html
Default layout: hero (if entry point) → content-block → cta
Index: no
Frontmatter: title, description
Notes: root-level one-off pages. Layout varies by page purpose.

## post
Path: src/posts/
Partials: partials/posts/
Default layout: post-header → body-text → tag-list
Index: yes → partials/posts/index.html
Index layout: post-listing → (post-list-item)* reverse-chronological
Frontmatter: title, date, tags, summary
Notes: single column, readable width, no hero.
```

Always include a `page` type for root-level one-off pages. Add additional types from the interview.

For each type with `Index: yes`, specify the index layout.

For each root-level page, add a one-line **Job**: the one thing this page is for, and — when its subject matter could overlap another planned page's — what it must NOT repeat. This is what lets `/b2:write` and `/b2:website-review` catch two pages drifting into the same story later, instead of a human having to notice it after the fact:

```markdown
## page
...
Pages:
- index.md — Job: state the core pitch and route deeper. Not: a step-by-step walkthrough (how-it-works.md owns that).
- how-it-works.md — Job: the literal step-by-step process, in full detail. Not: the pitch (index.md owns that).
```

Skip the Job line for pages with no realistic overlap risk (e.g. a standalone contact page) — this is only worth recording where two pages could plausibly converge on the same content.

The semantic class names in "Default layout" and "Index layout" are suggestions — use names that describe the content, not the style (`.post-header` not `.dark-header`).

---

## Creating Stub Files

After writing content-types.md, create stub markdown files:

**Root pages** in `website/src/`:
```markdown
---
title: About
description: About [site name].
---

*[About page content goes here. Run /b2:write to generate copy.]*
```

**Typed content** — create `website/src/{type}/` subfolder and 1–2 example stubs:
```markdown
---
title: Example Post Title
date: YYYY-MM-DD
tags: []
summary: Brief summary of the post.
---

*[Post content goes here. Run /b2:write to generate copy.]*
```

Use the correct frontmatter fields from the content type's spec in content-types.md. Every stub must have all required frontmatter.

---

## After Writing

Update `website/docs/status.md` — mark Structure complete:
```
- [x] Structure → website/docs/content-types.md
```

Tell the user:
- File paths created
- How many stub files created
- "Run `/b2:write` next — write real content before design so mockups use your actual copy, not stubs."
