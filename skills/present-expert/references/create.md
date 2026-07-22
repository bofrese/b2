# Create Workflow

There are four phases. Do not skip ahead. Generate markdown only when the idea is concrete — not before.

---

## Phase 1: Context Harvest

### Read b2 docs silently

Before saying anything, read any of these that exist (Read tool, skip silently if absent):

- `docs/product/vision.md`
- `docs/product/website-design-brief.md` (fall back to `docs/product/design-brief.md`)
- `docs/product/personas.md`
- `docs/notes/README.md` — if found, scan for relevant category files and read those too

Do not mention this step. Use what is found to skip redundant questions or probe deeper where docs give partial answers.

### Open the conversation

Ask three things (one message):

1. **The occasion** — "What's the context? Conference talk, internal team, investor pitch, client workshop — what are we building for?"
2. **Duration** — "How long do you have?"
3. **Background material** — "Any material I should start from? URLs, files, notes, an earlier draft — throw it at me."

### Harvest material

- URL → WebFetch. Extract by section, ignore nav/footer/boilerplate.
- File path → Read tool.
- Pasted text → accept as-is.

Anything substantial (research notes, a rough draft, competitor decks) goes into
`docs/presentations/{slug}/work.md` once the slug is known (see Phase 4) rather than being folded
straight into the deck — keeps working material separate from the polished markdown, same
separation `/b2:talk` keeps from `docs/product/vision.md`.

After harvesting, give a brief inventory — what exists and what's missing:

> "Here's what I'm working with: a product vision (clear on audience, vague on the villain), a design brief (strong visual language), no personas. A few things to probe before we structure this..."

Move directly into Phase 2.

---

## Phase 2: Strategic Interview

Read `references/interview-guide.md` now. Follow it exactly.

The interview covers 7 questions: the ONE thing, the audience, the goal, the enemy, the proof, the hook, and the three movements. Each has specific push-back rules for the failure modes.

End with the synthesis check. Do not proceed to Phase 3 until the user confirms the synthesis is correct.

---

## Phase 3: Outline Approval

From the confirmed synthesis, propose a slide-by-slide arc in this format:

```
**Working title: [title]**
Duration: ~[N] slides / [N] minutes

1. **[Slide name]** — [one line: what this slide does, not what's on it]
2. **[Slide name]** — [...]
...

---
Opening words: "[proposed first sentence]"
Closing words: "[proposed last sentence — echoes the opening]"
```

Then ask: "What's wrong with this order? What's missing? What's in the wrong place?"

Ordering rules:
- Slide names are active claims, not labels.
- The enemy appears before the solution — tension before resolution.
- The proof comes after the audience understands what's at stake.
- The CTA is last. The close echoes the open.
- Minimum viable slide count. More slides is not more persuasion.

Iterate until the user explicitly approves. Do not generate markdown until you have a clear "yes, let's write it."

---

## Phase 4: Generate Markdown

### Before writing

Ask:
- Filename slug (or derive from title: lowercase, hyphens, no special chars)
- Transition style (default: `slide`)

Do not ask about theme here — theme resolution happens automatically below, after the file exists.

Run:
```bash
root="$(pwd)" && mkdir -p "$root/docs/presentations/{slug}/assets"
```

If Phase 1 collected working material not directly used in the deck, write it to
`docs/presentations/{slug}/work.md` now.

### Write the file

Read `references/slide-format.md` now. Follow all rules there for titles, body content, visual comments, and presenter notes. Leave `theme:` frontmatter unset for now — the theme-resolution step below fills it in.

Write to `docs/presentations/{slug}/{slug}.md`.

### After generating

Tell the user the file path. Then:

> "Read through the flow. What's not right? What's missing, weak, or in the wrong place?"

Iterate — rewrite individual slides, reorder, cut, or add — until the user says it's done. The goal: a file that could be handed to an AI image generator and a speaker and produce a great presentation.

### Theme resolution

Once the user is satisfied with the content:

```bash
root="$(pwd)" && ls "$root/website/presentation-themes/" 2>/dev/null
```

- **No themes exist:** tell the user "No presentation theme yet." and offer to dispatch
  `present-design-expert` now (see Dispatch below). Leave `theme:` unset in the frontmatter.
- **Exactly one theme exists:** write its name into the deck's `theme:` frontmatter silently, and
  mention it: "Using your `{name}` presentation theme."
- **Multiple themes exist:** ask which one, defaulting to the most recently created (by directory
  mtime). Write the chosen name into `theme:`.

### Dispatch

After theme resolution, offer to continue:

- **If no theme was resolved:** "Want me to kick off `/b2:present-design` now to create one? (yes/no)"
  - Yes → use the Skill tool to invoke `present-design-expert`.
  - No → "Run `/b2:present-design` whenever you're ready, then `/b2:present-build {slug}` to render this deck."
- **If a theme was resolved:** "Ready to render this into a live deck? I can run `/b2:present-build {slug}` now. (yes/no)"
  - Yes → use the Skill tool to invoke `present-build-expert`, passing `{slug}`.
  - No → "Run `/b2:present-build {slug}` when you're ready."
