# Review Loop — Session Procedure

## Verify the server first

Screenshots need the deck served, not opened via `file://` (relative asset paths and reveal.js's
own routing depend on a real origin). Reuse the browser-detection order `website-review-expert`
already established — MCP browser tools → `npx playwright` → `playwright` CLI → halt with install
instructions. If a local server for this project isn't already running, offer `/b2:serve`.

Navigate to `http://{host}/presentations/{slug}/#/{slide-id}` to land directly on a given slide.

---

## Mode: one by one (default)

For each slide, in deck order (or starting from a named slide):

1. **Read** the slide's current markup from the built `index.html` and its source block in the
   `.md`.
2. **Screenshot** it at rest, and step through every fragment (see "Verifying reveals" below).
3. **Critique** against all five dimensions in `references/checklist.md`. Write the critique as a
   design director would: name the concrete defect, not a vague impression. Silence is not
   feedback — if a dimension is genuinely fine, say so in one clause and move on, don't pad.
4. **Propose** a specific plan — not "this could be improved" but the actual headline rewrite, the
   actual component to use, the actual fragment structure. If there are two reasonable directions,
   give a recommendation and one sentence on the tradeoff; don't present an open-ended menu for
   something with an obvious better answer.
5. **Wait for confirmation.** This is the one non-negotiable step — never implement a content or
   design change to a presentation slide without the presenter's go-ahead, even when the fix seems
   obviously correct. A quick "yes, go ahead" is enough; don't require a detailed sign-off on
   something already clearly proposed.
6. **Implement**, then **verify** (see below).
7. **Sync the `.md` source** so it matches what got built (see "Syncing back to source").
8. Move to the next slide. Don't re-ask which mode to continue in — keep going until the deck ends,
   the user stops, or a jump is requested.

## Mode: whole-deck batch

Same five-dimension critique as one-by-one, but run it across every slide (or every slide in a
named act/section) before proposing anything. Present the full findings list in one message,
grouped by slide, each finding tagged with its dimension and a one-line fix. Wait for the user to
say which findings to act on (a range, "all of them," specific numbers, or "skip the typography
ones"). Implement the approved set together, then verify each changed slide individually — batch
verification (visual only, not one-by-one confirmation) is appropriate here since the user already
approved the whole set.

Use this mode when the user asks for an overview before committing to detailed work, or when
they've already reviewed most of the deck in a prior session and want a targeted list of what's
left.

## Mode: jump to specific slides

Resolve the named slide(s) or topic to slide id(s) — search the `.md`'s headlines/content if the
user names a topic rather than an id. Run the one-by-one loop, but only for the named slides, in
the order given (or deck order if unspecified).

---

## Verifying reveals

**A direct navigation to a slide's hash shows every fragment already revealed** — reveal.js does
this on purpose so a deep link isn't missing content. To check the *entering* state (nothing
revealed) and step through fragments one at a time, reset in-browser first:

```js
Reveal.slide(Reveal.getIndices().h, 0, -1)   // -1 = no fragments shown yet
Reveal.next()                                 // advances one fragment
```

Take a screenshot after each step, not just at rest and at "everything shown."

**Screenshots taken immediately after a navigation or fragment step can land mid-transition** and
show an artifact that isn't a real bug (e.g. content appearing shifted during a slide-change
animation). Wait ~300-600ms after the action before capturing, or when the actual concern is
animation *timing* itself (not just the resting visual), sample computed styles at several
timestamps in one batched `evaluate` call instead of trusting screenshot timing:

```js
async () => {
  const el = document.querySelector('...');
  const start = performance.now();
  const samples = [];
  while (performance.now() - start < 1200) {
    samples.push({ t: performance.now() - start, value: getComputedStyle(el).someProperty });
    await new Promise(r => setTimeout(r, 100));
  }
  return samples;
}
```

This is the only reliable way to confirm a custom transition (a colour fade, a delayed second
element) actually runs on the timeline intended — a single screenshot at an arbitrary point proves
nothing about sequencing.

**Check at least two viewport heights** (e.g. 1440×900 and 1440×700) for any slide with real
content, not just the one the browser happened to open at — a short-viewport crop is one of the
most common defects found this way, and it's invisible at a comfortable window size.

**Force a hard reload after any CSS change** (`location.reload(true)` or navigate fresh) before
re-screenshotting — a served stylesheet can stay cached in an already-open tab even after the file
on disk changes, producing a false "the fix didn't work" read. If a fix genuinely doesn't appear to
take effect after a hard reload, `curl` the served bytes and compare against the file on disk before
assuming the code itself is wrong.

---

## Implementing a change

Edit `website/dist/presentations/{slug}/index.html` directly for the slide's markup/inline styles.
If the fix is a shared component or token (a reusable size class, a fixed CSS bug), edit
`website/presentation-themes/{theme}/theme.css` instead and re-copy it to
`website/dist/presentations/shared/themes/{theme}/theme.css` — the same two-file discipline
`present-build-expert` follows, since editing only the dist copy means the next full rebuild
silently reverts the fix.

## Syncing back to source

After a slide is accepted, update `docs/presentations/{slug}/{slug}.md`'s matching block so the
source reflects what was actually built — both the content (if copy changed) and its
`<!-- Visual: -->` comment (if layout/graphics/dynamics changed). This is what keeps a future
`/b2:present-build` reconcile pass from misreading the slide as unchanged, or worse, regenerating
it back to the pre-review version. Treat this the same as `present-build-expert`'s own accept step
— one accept covers both files, no separate sync-permission prompt needed since the presenter just
approved the rendered result.

## Final report

After a mode completes (one-by-one reaching the end, batch finishing its approved set, or a jump
finishing its named slides), report:

```
Reviewed: N slides ({mode})
Changed: N slides — {one-line list, slide id + what changed}
Bugs found & fixed: N (see capture-ratchet note in SKILL.md if any)
Verification: console clean across N slides; checked at 900px and 700px heights

Live at: website/dist/presentations/{slug}/index.html
```
