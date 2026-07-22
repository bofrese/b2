# Phase 1 — Interview and Direction Proposals

Read `${CLAUDE_PLUGIN_ROOT}/shared/design/presentation-design.md` using the Read tool now — it
grounds the motion-intensity and stage-context questions below in real stage/pacing judgment
rather than generic aesthetic preference.

---

## Interview

The Prerequisite Check already read the website's `design.md` and `decisions.md` — confirm what
they establish back to the user in 2-3 lines ("Your site's design language is {summary} — the
presentation theme will read as an extension of this, not a departure.") before asking anything.

Ask these directly (presentation-specific, not in the shared question bank):

1. **Stage context** — "Where will these get presented — a conference stage, a client meeting room, a webinar, all of the above? This affects type size and contrast."
2. **Motion intensity** — "How dynamic should this feel: minimal (clean, mostly static, motion only where it earns its place), moderate (purposeful transitions and reveals), or dynamic (confident use of animation/3D as a visual signature)?"
3. **Audience** — "Who's usually in the room — technical peers, executives, prospective clients, a mixed public audience?"

Do not re-ask anything the website's `design.md`/`decisions.md` already answers (colour, typography,
brand personality) — those carry forward directly.

After the interview, write phase transition to `website/docs/status.md`:
```
- [ ] Present Design  → IN PROGRESS
  phase: directions
```

---

## Direction Proposals

Read `${CLAUDE_PLUGIN_ROOT}/shared/design/styles-and-business.md` (and `trends.md` if proposing
current directions). Study the website's design language plus the interview answers, and propose
**2-3 distinct directions** — fewer than a website redesign's 5, since presentation iteration is
lower-stakes and faster.

Each direction must read as a **stage adaptation of the existing website design**, not a fresh
palette — same colour/typography/brand character, reinterpreted for the presentation register
(larger type, higher contrast, more breathing room, the chosen motion intensity).

For each direction:
- **Name** — a memorable label (e.g., "Site, Amplified", "Quiet Confidence", "Kinetic Brand")
- **Visual keywords** — 3-4 specific descriptors
- **Interpretation** — 1-2 sentences: how this direction expresses the brand at presentation scale
- **Motion approach** — how it delivers the chosen intensity level concretely (what animates, what
  stays still)

Present all directions, then ask:

> "Want me to mock up all of these, or narrow first?"

Wait for **explicit** confirmation — "mock them up", "go ahead", "proceed", or naming which ones to
cut. Plain acknowledgment without a clear go/no-go ("ok", "sounds good", "looks fine") is not
sufficient; ask again which directions to mock up. 2-3 is fine to mock up directly; narrow only if
the user explicitly wants to cut one.

Once confirmed, write the chosen direction names and descriptions to `website/docs/status.md`:

```
  phase: mockups
  directions:
    - concept-1: {Name} — {one-line description}
    - concept-2: {Name} — {one-line description}
```

Then load `references/mockups.md` and continue with the mockup phase.
