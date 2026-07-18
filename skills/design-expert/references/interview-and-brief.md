# Phases A, B, B2 — Interview, Brief, and Direction Proposals

---

## Phase A1 — Document-aware grounding

Before asking anything, ground yourself in what already exists. The product-level docs were read in the Prerequisite Check (`vision.md`, `personas.md`, product `design-brief.md`). Confirm what they establish, then ask **only the gaps**.

1. Read `${CLAUDE_PLUGIN_ROOT}/shared/design/interview-questions.md` — the shared question bank (business & goals, audience, competitive context, content & conversion).
2. From the docs already read, extract what is answered: audience, positioning, brand personality, primary action/conversion intent, success metric.
3. Confirm your understanding back to the user in 2–4 lines ("Here's what I already know from your docs: … — correct?").
4. Ask **only** the genuinely unanswered questions from the bank — typically business goals/success metric, competitive context, and conversion intent when the docs are silent. Do **not** re-ask audience or positioning that a doc already answers.

If `docs/product/*` is sparse, fall back to asking the relevant bank questions directly — degrade gracefully, never assume an answer.

### Brand assets

Ask: **"Do you have any brand assets to use in the design — a logo, photos, illustrations, icons, a background image? If so, drop them into `website/mockups/assets/` and tell me what's there."**

- If yes: ensure the folder exists (`mkdir -p website/mockups/assets`), then list what the user placed there and note each filename + what it is (logo, hero photo, …). These get passed to the mockup agents so concepts use the real assets, and are carried into the theme in Phase E so they appear on the live site.
- If no: mockups use CDN icon/image placeholders (Lucide). Assets can still be added later via `/b2:illustrate` or `/b2:write`.

Then proceed to Phase A2.

---

## Phase A2 — Aesthetic Interview

**Existing-site seed:** Check for `website/docs/site-import/design-brief.md` (Read tool; tolerate
FileNotFoundError). If present (written earlier by the site-import Design capability, via
`talk-expert`/`write-expert`/`structure-expert`'s trigger), open this phase differently: summarise
its colour/typography/layout impressions and any screenshots, then ask "Here's your current site's
look — what do you like about it, and what doesn't work? We can carry the parts that work into one
of the mockup concepts instead of starting from nothing." Use their answer to steer questions 1-6
below toward gaps only — don't re-ask what the brief already shows and the user just confirmed they
like. If the file is absent, run the interview as written below.

Conduct the interview one question at a time. Wait for answers before asking the next.

1. **Style direction:** "How do you want this site to feel? Think in adjectives: minimal, warm, editorial, bold, playful, refined, technical, human. What words resonate?"

2. **Visual references:** "Give me 2–3 websites you love the look of — not in your industry necessarily, just sites you find visually good. What do you like about them?"

3. **Colour:** "Any colours that feel right — or colours that are definitely wrong? Think about your existing brand if you have one, or just instinct."

4. **Typography:** "Serif (classic, editorial) or sans-serif (modern, clean)? Heavy or light? Any fonts you've seen and liked?"

5. **Density:** "Dense with information, or generous whitespace? Would you rather a visitor sees everything above the fold, or scroll through a more spacious layout?"

6. **Key emotion:** "What's the one feeling you want a visitor to have when they land on this site?"

After the interview, write phase transition to `website/docs/status.md`:
```
- [ ] Design  → IN PROGRESS
  phase: brief
```

Then proceed directly to Phase B.

---

## Phase B — Written Design Brief

Synthesise the interview into a written brief before generating anything. Present the brief and wait for explicit approval.

The brief must include:
- **Business context** — audience, positioning, primary conversion intent, and success metric (from Phase A1). When a product `design-brief.md` exists, note explicitly how the website stays consistent with it.
- **Style direction** — 2-3 sentences describing the visual feeling
- **Colour palette** — 3–5 colours with roles (primary, secondary, accent, background, text)
- **Typography** — headline font + body font, with reasoning
- **Layout approach** — generous or dense, hero-led or content-led, etc.
- **Key design principles** — 3 principles that guide every design decision
- **Per-content-type treatment** — for each type in `content-types.md`, describe the visual treatment for item pages and index pages (if applicable)

End with: "Does this match your vision, or is anything off?"

Do not proceed to Phase B2 without explicit approval. "Looks good, but can you change the typography?" is feedback, not approval.

On approval, update `website/docs/status.md`:
```
  phase: directions
```

Then proceed to Phase B2.

---

## Phase B2 — Design Direction Proposals

Act as art director. First read `${CLAUDE_PLUGIN_ROOT}/shared/design/styles-and-business.md` (and `trends.md` if proposing current/2026 directions) for the style→business mapping. Study the approved brief holistically — brand character, emotional intent, audience, business context, and content types — and propose **5 distinct design directions** drawn from your full knowledge of visual design styles and movements.

If Phase A2 surfaced an existing-site brief the user was generally positive about, make one of the 5 directions a refined rebuild of that look — same palette/typography/layout impression, executed in clean, maintainable, semantic CSS — rather than five directions that all discard it.

For each direction:
- **Name** — a memorable label (e.g., "Swiss Precision", "Dark Editorial", "Organic Warmth")
- **Visual keywords** — 3–4 specific descriptors (e.g., "uppercase tracking, tight grid, cold palette")
- **Interpretation** — 1–2 sentences: how does this direction express the brand?
- **Business fit** — one honest sentence grounding the direction in the business context (audience expectation × brand personality × conversion goal, per `styles-and-business.md`), not aesthetics alone — or a tension to watch.

After presenting all 5, name your **top 3 recommendations** and briefly justify the ranking. Then ask:

> "These are the three directions I'd take to mockup. Want to proceed with these, or swap any out?"

Wait for explicit confirmation. The user may adjust the selection.

Once confirmed, write the three chosen direction names and descriptions to `website/docs/status.md`:

```
  phase: mockups
  directions:
    - concept-1: {Name} — {one-line description}
    - concept-2: {Name} — {one-line description}
    - concept-3: {Name} — {one-line description}
```

Then load `references/mockups.md` and continue with Phase C.
