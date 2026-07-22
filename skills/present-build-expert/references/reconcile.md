# ID Backfill and Reconcile

No scripted diff/patch engine — this mirrors `sync-expert`'s established pattern exactly: get a
git diff, then read and reason about what it means. Slide-id classification is AI-interpreted, not
algorithmic.

---

## Parsing slide boundaries

Split the deck's body on lines that are exactly `---` (horizontal separator only — never split on
`--`, which isn't used in this dialect). Each resulting block is one slide. A slide's id, if
present, is in its first `<!-- .slide: ... -->` comment (may also carry `data-visibility="hidden"`
in the same comment).

---

## ID Backfill

Run on every build, before anything else, on **every** slide in the current file:

1. For each slide missing an `id="..."` attribute in its `.slide:` comment (or missing the comment
   entirely): generate a slug from its first heading text (lowercase, hyphenate, strip non-alphanumerics).
   If empty/untitled, or the slug collides with another slide already assigned in this pass,
   append a numeric suffix (`-2`, `-3`, ...); if still colliding after a few attempts, fall back to
   a short random suffix.
2. For each slide that **already has** an id: check it isn't a duplicate of another slide's id in
   this same file (the copy-paste case — a user duplicated a slide block including its id comment).
   If a duplicate is found, reassign a fresh id to the **second and later** occurrence using the
   same slug generation as step 1; the first occurrence keeps its original id.
3. Write every newly assigned/reassigned id back into the source markdown (Edit tool, one comment
   per touched slide — insert `<!-- .slide: id="{slug}" -->` if the slide had no comment at all, or
   add the `id="{slug}"` attribute into an existing `.slide:` comment that only had e.g. `hidden`).

Report at the end of the build: "Assigned IDs to N slides" (only if N > 0 — silent if every slide
already had one).

**Why this can't cause a false "changed" verdict on an untouched slide:** backfill only touches a
slide that either had no id (so it can't already exist in the prior output's `data-slide-id`
values — it's classified "new" regardless of the diff noise from inserting the comment) or a
duplicate id (the reassigned copy is likewise absent from the prior output under its old shared
id — also "new"). A slide that was already correctly identified and unchanged never gets touched by
backfill, so its diff stays clean. Backfill always runs before the stale-check diff below; this is
safe by construction, not by ordering luck.

---

## Stale check and reconcile decision

```bash
root="$(pwd)"
slug="{slug}"  # substitute actual slug
md_file="docs/presentations/$slug/$slug.md"
dist_html="website/dist/presentations/$slug/index.html"

if [ ! -f "$root/$dist_html" ]; then
  echo "no-prior-build"
else
  if git -C "$root" rev-parse --git-dir >/dev/null 2>&1; then
    last_commit=$(git -C "$root" log -1 --format="%H" -- "$dist_html" 2>/dev/null)
    if [ -n "$last_commit" ]; then
      echo "=== Changes since last build (committed + uncommitted) ==="
      git -C "$root" diff "$last_commit" -- "$md_file"
    else
      echo "=== Output not in git — uncommitted changes only ==="
      git -C "$root" diff HEAD -- "$md_file"
      git -C "$root" status --short -- "$md_file"
    fi
  else
    echo "no-git"
  fi
fi
```

**One diff call, one coordinate system.** `git diff "$last_commit" -- "$md_file"` compares that
commit's version of the file directly against the current working tree in a single hunk set — this
is deliberately *not* two separate diffs (`commit..HEAD` plus `HEAD..working-tree`), which would
produce hunks in two different coordinate systems (one relative to HEAD's copy, one relative to the
working-tree copy) that cannot be correctly overlaid onto "line ranges in the current file" without
translation. One call, one file version to compare against, no translation needed.

**`no-prior-build`** → full generate (see `render.md`): every slide is authored fresh, no reconcile needed.

**When classification confidence is degraded, regenerate rather than preserve.** This applies
whenever the diff can't be fully trusted — `no-git` (no repository at all), the output-untracked
branch above only sees uncommitted changes and can't see committed history since the actual last
build, or any case where a slide's change status is genuinely ambiguous from the diff. Regenerating
an unchanged slide costs wasted rework that's visible and reported (a slide that looks identical
after rebuild); wrongly preserving a changed slide costs silent staleness with no visible signal at
all. Default to the recoverable mistake.

**Prior build exists** → use the diff output plus the current file to classify every slide id:

- **Unchanged** — the id exists in both the current source and the existing
  `website/dist/presentations/{slug}/index.html` (as `<section data-slide-id="{id}">`), and no diff
  hunk falls within that slide's line range in the current file. Copy that `<section>` block from
  the existing output **verbatim** into the new output, at its position in the current file's
  order.
- **Changed** — the id exists in both, but a diff hunk falls within its line range. Regenerate that
  slide's HTML (sequential pass, `render.md`).
- **New** — the id exists in the current source but not among the existing output's
  `data-slide-id` values. Generate it fresh.
- **Moved** — the id exists in both, but its position among the other ids has changed. **Detect
  this by content identity, not hunk absence:** a plain line-based `git diff` reports a moved block
  as a delete-hunk at its old position *and* an insert-hunk at its new one — both positions show
  diff activity, unlike a genuinely unchanged slide, so the "no hunk in range" test used for
  Unchanged does not apply here. Instead, extract this id's slide block (markdown source, by its
  `.slide:` id comment) from *both* revisions being compared — `$last_commit`'s version of
  `$md_file` and the current working tree's version — and compare them directly, independent of
  where either hunk lands. If that markdown block is textually identical in both revisions (only
  its position among sibling slides differs), classify as moved, not changed. Relocate the existing
  `<section>` block (from `website/dist/presentations/{slug}/index.html`) to its new position; do
  not regenerate its content.
- **Removed** — an id exists in the existing output's `data-slide-id` values but not in the current
  source at all. Drop that `<section>` from the new output.

If the diff is empty but the mtime check suggested staleness (rare — e.g. a touched but unchanged
file), treat every slide as unchanged; nothing to regenerate.

Output slide order always follows the **current source file's** order, regardless of each slide's
classification.
