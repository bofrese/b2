# Style Brief - Phase 1

Run this phase only on first use (when `docs/product/illustration-style.md` does not exist).

---

## Load Site Context

Read these files. Skip gracefully if missing - adapt to what's available:

1. `docs/product/vision.md`
2. `docs/product/website-design-brief.md` (fall back to `docs/product/design-brief.md`)
3. `website/docs/decisions.md`
4. If `website/b2.cfg` exists, extract `THEME=` then read `website/theme/{THEME}/design.md` if it exists

Note the site's purpose, audience, personality, any humour signals, and visual register.

---

## Style Interview

Ask one or two questions at a time. Adjust subsequent questions based on answers.

1. "Looking at your site - [summarise the vibe from the docs in one sentence]. Does that feel right, or is there something the docs miss about the personality you're going for?"

2. "When someone lands on one of your illustrated pages, what should they feel in the first three seconds? Give me an adjective that isn't 'professional' or 'clean'."

3. "What's the humour register? Dry wit? Warm and playful? Deadpan? None?"

4. "Any visual references - websites, illustrators, magazines, book covers, films? Anything in the neighbourhood you want to be in." (Accept URLs → fetch with WebFetch. Accept names → ask what specifically appeals.)

5. "What should illustrations *never* look like on this site? Name a style or feeling to avoid."

6. "Illustrations will mostly appear as [infer from context: hero images / article headers / spot illustrations / social cards - confirm]. Right?"

---

## Propose Three Style Directions

Based on the interview and site context, propose exactly three distinct directions. For each:

- **Name** - evocative, not "Option A"
- **Style lineage** - art movement, medium, or illustrator tradition
- **Visual description** - palette range, line weight, texture, rendering, mood
- **Why it fits this site specifically** - connect to what was learned. No generic claims.
- **What it would not suit** - honest limitations
- **A sample prompt** - one example, written ready to generate

State a clear preference if one direction is strongest, with reasoning. Wait for selection or a request to iterate.

---

## Write the Style Brief

Once a direction is chosen (or blended), write `docs/product/illustration-style.md`:

```markdown
# Illustration Style Brief
*Established: YYYY-MM-DD*

## Style: [Name]

### Character
[2–3 sentences: what this style feels like and what it says about the site]

### Visual Language
- **Medium / rendering:** [e.g. flat vector with paper texture overlay; no gradients]
- **Line quality:** [e.g. confident, slightly imperfect hand-drawn edges; 2–3px weight]
- **Colour palette:** [specific - name colours or approximate hues]
- **Lighting:** [e.g. flat graphic; no drop shadows; subtle inner highlights only]
- **Texture:** [e.g. subtle grain overlay; risograph halftone dots at 15%]
- **Perspective:** [e.g. slight isometric tilt on objects; characters always front-facing]
- **Characters / figures:** [e.g. abstract geometric; no faces; hands expressive]
- **Typography in image:** [e.g. avoid text in images / hand-lettered only]

### Mood and Personality
[Feeling this style conveys; the humour register; what it should never feel like]

### Prompt Formula
Repeatable structure for this style:
[Subject + action] [environment] [composition] [medium and style] [palette] [lighting] [texture] [mood] [quality markers]

Example:
"[full ready-to-use example prompt in this style]"

### Avoid
- [list visual tropes and styles to never use]
```

Confirm: "Style brief saved to `docs/product/illustration-style.md`. Ready to illustrate - give me a page, article, or concept."
