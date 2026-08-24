# Typography Audit — Deck-Wide Consistency Sweep

Offer this as a distinct option early in a review session ("want me to also audit the whole deck's
typography for consistency?") rather than only catching size drift slide-by-slide — one-off sizes
are easy to miss individually and only become an obvious problem in aggregate.

## Step 1 — Run the script

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/present-review-expert/scripts/audit-typography.sh" website/dist/presentations/{slug}/index.html
```

This reports every distinct `font-family` and `font-size` declaration found in the built deck,
sorted by frequency. Read the output looking for **the same semantic role expressed multiple
slightly-different ways** — e.g. a "paragraph under a headline" role showing up as eight or nine
near-identical `clamp()` values across different slides. That's the signal a reusable token is
missing, not that the content genuinely needed that many distinct sizes.

## Step 2 — Cross-check against the documented system

Read the theme's `design.md` Typography System table. Confirm:
- Every font-family in the audit output is one of the table's documented families. A stray one is
  almost always a copy-paste leftover.
- The table's documented sizes actually match what the corresponding CSS class implements (spot
  check at least the most load-bearing rows — headings, bullets, body). Documentation drifts from
  implementation over time; a mismatch found here is worth fixing in the doc regardless of whether
  it's also fixed in code.

## Step 3 — Define missing tokens

For each recurring-but-undocumented role found in Step 1, define one reusable class in the theme's
`theme.css` (not the deck's own bespoke `<style>` block — this belongs to every deck on the theme,
and a second deck will need the same role eventually). Two roles come up in almost every deck:

- **A lead/intro paragraph under a headline** — one canonical size, not a bespoke clamp per slide.
- **Secondary/supporting text** (a caption, a smaller closing line, a muted aside) — same
  principle, one size.

```css
.lead-text{
  font-family:'{body font}', serif; font-weight:300;
  font-size:{one clamp value}; color:var(--text-mid); line-height:1.6;
}
.sub-text{
  font-family:'{ui font}',sans-serif; font-weight:500;
  font-size:{one fixed value}; color:var(--text-mid); line-height:1.6;
}
```

**Narrow-column scoping.** If the theme has a split text/image layout (a narrower text column
alongside a full-height image), that column needs a half-step-down size or the same token wraps
awkwardly there. Scope by ancestor, not a second class name, so a slide's markup never needs to
know which layout context it's in:

```css
.text-col .lead-text{ font-size:{smaller clamp}; }
.text-col .sub-text{ font-size:{smaller fixed value}; }
```

**Check every layout wrapper that hosts body text, not just the most common one.** A deck can have
more than one narrow-column context (a named split-layout class, a centred-hero layout with its own
text wrapper, etc.) — each one that currently uses `.lead-text`/`.sub-text` needs its own scoped
override, or that slide silently falls back to the full-width size and re-wraps taller than
before. This was the one real regression found doing this sweep the first time: a second layout
wrapper existed alongside the primary split-layout class, wasn't given the same override, and
one slide's paragraph grew from two lines to three until it was caught by an intermediate
screenshot check — verify every affected slide individually after the sweep, don't assume the fix
is complete just because the common case is covered.

## Step 4 — Sweep and verify

Replace each matching bespoke inline `font-size`/`font-family`/`color`/`line-height` block with the
new class, preserving any other inline properties (`max-width`, `margin-top`, etc.) that aren't
part of the token itself. Do this as precise, individually-verified replacements — matching on the
exact old style string per instance — rather than a broad regex across the whole file, since a
loose pattern can also catch preserved/unrelated slides that happen to share a similar-looking
inline style for a different reason.

After the sweep:
1. Copy the updated `theme.css` to `website/dist/presentations/shared/themes/{theme}/theme.css`.
2. Re-screenshot every changed slide (not just one representative one) at both a normal and a short
   viewport height, hard-reloading first (see `references/review-loop.md`'s caching note) — confirm
   each one still matches its previously-approved layout, since the whole point of this sweep is
   that it should be visually silent, not a redesign.
3. Run a full-deck console sweep (navigate every slide, step every fragment, confirm zero errors) —
   a CSS specificity mistake introduced during the sweep (a new rule losing to an existing one, or
   vice versa) shows up as a silent visual regression, not a console error, so the screenshot check
   in step 2 is the real verification; the console sweep only catches unrelated breakage.
4. Fix the theme's `design.md` Typography table to document the new tokens and their exact values,
   in the same table as the existing documented roles.
