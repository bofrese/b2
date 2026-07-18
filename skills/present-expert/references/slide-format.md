# Obsidian Advanced Slides Format Reference

## File Template

```markdown
---
theme: [theme]
transition: [transition]
slideNumber: true
---

# [Title]
## [Subtitle or hook line]

<!-- Visual: [specific description] -->

note:
[What to say — not what's on the slide. Include: tone to open with, any story or anecdote, transition to next slide.]

---

## [Slide title as active claim]

[Minimal body content — one idea, max 3 lines or bullet points]

<!-- Visual: [specific description] -->

note:
[What to say. End with: Transition: "This brings us to..."]

---
```

**Theme options:** `default`, `black`, `white`, `moon`, `sky`, `solarized`
**Transition options:** `none`, `fade`, `slide`, `convex`, `zoom`
**Slide separator:** `---` (horizontal only — keep the flow linear)

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

Notes are for the speaker, not a summary of the slide.

Include:
- The story or specific example to tell here
- The exact words for a key phrase worth saying precisely
- How to handle likely pushback or a confused look
- A transition sentence to the next slide

Format: Transition line at the end of every note.
```
note:
Tell the story of [specific client/event]. The punchline is not the data — it's what happened after. Pause after "nobody believed it."

Transition: "Which is why the question we should be asking isn't how, but whether."
```

Notes should be substantial enough that a colleague could deliver the talk from them.

### Opening slide

Never a title-only slide. The hook goes here — the first words the speaker says are in this slide's note and should be the provocation, not an introduction.

### Closing slide

Not "Thank you." Not "Questions?" The final slide is the call to action, and it echoes the opening. The loop closes.

If the opening slide asked a question → the closing slide answers it.
If the opening made a claim → the closing returns to it with proof behind it.
