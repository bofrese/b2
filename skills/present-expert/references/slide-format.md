# Presentation Markdown Format Reference

Reveal.js's native external-markdown dialect — the same primitives reveal.js's own markdown
plugin parses, and what Obsidian's Slides Extended plugin previews. No bespoke syntax is invented;
every directive below is a native reveal.js comment attribute.

## File Template

```markdown
---
theme: [name of a locked presentation theme, from website/presentation-themes/ — left unset if none exists yet]
transition: [transition]
slideNumber: true
---

<!-- .slide: id="opening-hook" -->
# [Title]
## [Subtitle or hook line]

<!-- Visual: [specific description] -->

Note:
- [keyword]
- [keyword]

[What to say — not what's on the slide. Include: tone to open with, any story or anecdote, transition to next slide.]

---

<!-- .slide: id="slide-slug" -->
## [Slide title as active claim]

[Minimal body content — one idea, max 3 lines or bullet points]

<!-- Visual: [specific description] -->

Note:
[What to say. End with: Transition: "This brings us to..."]

---
```

**Slide separator:** `---` horizontal only — keep the deck linear. Never use `--` (reveal's
vertical-stack separator); a 2D grid of slides adds presenter-overview complexity this format
deliberately avoids.

**`theme:`** names a folder under `website/presentation-themes/`, created by `/b2:present-design`.
`/b2:present-build` resolves it (unset + one theme exists → uses it silently and writes it here;
unset + multiple exist → asks, defaults to most recent). Never hand-pick a built-in reveal.js theme
name — the theme is always one this project's `/b2:present-design` produced.

**Transition options:** `none`, `fade`, `slide`, `convex`, `zoom` (reveal.js built-ins — free to use
regardless of the locked theme, since transitions are a runtime setting, not a design asset).

## Native Slide & Element Attributes

These are reveal.js's own external-markdown comment directives — not a b2 invention. They work
identically whether previewed in Obsidian or rendered by `/b2:present-build`.

**Slide id** — every slide needs one for surgical rebuilds to track it across edits/moves/renames.
Never hand-write one; `/b2:present-build`'s ID-backfill pass generates and writes these in
automatically on first build. Once present, leave it alone — editing or deleting it breaks that
slide's identity across rebuilds.

```markdown
<!-- .slide: id="the-enemy" -->
```

**Hidden slide** — skipped in linear next/prev navigation and the slide count, but still rendered
and reachable: the presenter overview shows it distinctly and can jump to or promote it live (the
PowerPoint hidden-slide trick). `hidden ≠ confidential` — the slide still exists in the built HTML.
Combine with the id attribute in one comment:

```markdown
<!-- .slide: id="backup-data" data-visibility="hidden" -->
```

**Fragments** — reveal one element at a time within a slide (build a bullet list, step through a
diagram):

```markdown
<!-- .element: class="fragment" -->
```

## Client Variants (versioning/handouts)

A client-specific version of a deck is a full copy of the source folder to its own slug
(`docs/presentations/acme-kickoff/`), edited/trimmed for that engagement, built independently to
its own stable URL. No shared frontmatter list of variants — the copied folder *is* the variant.
Hide slides you don't want in that client's linear flow with the hidden attribute above; they're
still one click away in the presenter overview if you need them live. The same URL serves both the
live presentation and the after-the-fact handout — there is no separate export.

---

## Slide Writing Rules

### Titles — active claims, not labels

Bad → Good:
- "Current Approach" → "We're building for the wrong person"
- "Solution" → "One change that fixes all three problems"
- "Background" → "Everyone in this room believes something false"
- "Conclusion" → "You already have everything you need"

Titles should complete the sentence: *"After this slide, the audience believes that..."*

### Body content — as little as possible

The slide supports the talk. It does not replace it.

- One idea per slide.
- Maximum 3 bullet points. No sub-bullets. Ever.
- Bold the single most important word or phrase if it helps orientation.
- If the slide needs more than 3 lines of text, it contains more than one idea — split it.

### Visual comments — specific and useful

Give the AI image generator or designer something to work with. Vague comments produce generic images.

Bad:
```
<!-- Visual: use a relevant image -->
<!-- Visual: something powerful -->
```

Good:
```
<!-- Visual: split-screen — left: wall of dense text, right: single bold sentence. High contrast. -->
<!-- Visual: line graph showing flat growth for 5 years, then a sharp upward curve at the inflection point. No labels, just the shape. -->
<!-- Visual: photo of an empty stadium. Lights on. Nobody there. -->
<!-- Visual: close-up of a hand-written sticky note that reads "just ship it" -->
<!-- Visual: two identical doors side by side — one labelled "before", one labelled "after". Same door. -->
```

Describe: composition, mood, what's present, what's absent. Include contrast, scale, and emotional register when they matter.

### Presenter notes — what to SAY

Notes are for the speaker, not a summary of the slide. Written as `Note:` (reveal.js's native
notes marker — case-insensitive, but write it capitalized for consistency).

**Structure: keywords first, prose below.** The first block of lines in a `Note:` body — up to the
first blank line — is a plain bullet list of glanceable keywords, for a mid-talk glance. Everything
after that blank line is full rehearsal prose, ending with the `Transition:` line. No header labels
either block — the position (before/after the first blank line) is the convention.

Include in the prose:
- The story or specific example to tell here
- The exact words for a key phrase worth saying precisely
- How to handle likely pushback or a confused look
- A transition sentence to the next slide

Format:
```
Note:
- empty room
- lights on
- nobody came

Tell the story of the launch event where attendance was zero. The punchline isn't the number—it's
what happened after. Pause after "nobody believed it."

Transition: "Which is why the question we should be asking isn't how, but whether."
```

Carries straight into the rendered `<aside class="notes">` — no reveal.js-side handling needed,
this is authoring convention only.

Notes should be substantial enough that a colleague could deliver the talk from them.

### Opening slide

Never a title-only slide. The hook goes here — the first words the speaker says are in this slide's note and should be the provocation, not an introduction.

### Closing slide

Not "Thank you." Not "Questions?" The final slide is the call to action, and it echoes the opening. The loop closes.

If the opening slide asked a question → the closing slide answers it.
If the opening made a claim → the closing returns to it with proof behind it.
