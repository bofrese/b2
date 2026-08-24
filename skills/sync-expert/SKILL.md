---
name: sync-expert
description: This skill should be used when the user runs "/b2:sync", asks to "convert markdown to HTML", "sync the site", "update the partials", "my HTML is out of date", or wants stale .md files converted to .html in website/partials/. Performs stale detection, item conversion, and index file regeneration.
---

# b2 Sync Expert

Convert stale `.md` content files to semantic HTML layout files in `website/partials/`, mirroring the `src/` subfolder structure. Also regenerate index files for content types where any item is stale and `Index: yes`.

---

## Prerequisite Check

Read `website/b2.cfg` if it exists. Look for a `THEME=` line. Default: `THEME=b2`. Theme directory: `website/theme/{THEME}/`.

Check whether `website/theme/{THEME}/components.md` exists (Read tool). If missing, stop:

> "Run `/b2:design` first — sync requires a completed theme with components.md."

---

## Step 1 — Run Stale Detection

Run these bash scripts using the Bash tool from the project root. Use absolute paths to ensure correct operation regardless of working directory.

Prefer git-based detection over timestamps. Timestamps are unreliable after git operations (clone, checkout, pull). Git knows exactly what changed.

**Individual content files — git-first, mtime fallback:**
```bash
root="$(pwd)"
in_git=false
git -C "$root" rev-parse --git-dir >/dev/null 2>&1 && in_git=true

find "$root/website/src" -name "*.md" | while read md; do
  rel="${md#$root/website/src/}"
  html="$root/website/partials/${rel%.md}.html"

  # No partial → always stale
  if [ ! -f "$html" ]; then echo "item:$md"; continue; fi

  if $in_git; then
    src_rel="website/src/$rel"
    partial_rel="website/partials/${rel%.md}.html"
    last_partial_commit=$(git -C "$root" log -1 --format="%H" -- "$partial_rel" 2>/dev/null)

    if [ -n "$last_partial_commit" ]; then
      # Committed changes to src since last partial commit
      commits_since=$(git -C "$root" log --oneline "${last_partial_commit}..HEAD" -- "$src_rel" 2>/dev/null)
      # Uncommitted changes to src
      uncommitted=$(git -C "$root" diff HEAD -- "$src_rel" 2>/dev/null)
      [ -n "$commits_since" ] || [ -n "$uncommitted" ] && echo "item:$md"
    else
      # Partial not in git history — fall back to mtime
      [ "$md" -nt "$html" ] && echo "item:$md"
    fi
  else
    # Not a git repo — fall back to mtime
    [ "$md" -nt "$html" ] && echo "item:$md"
  fi
done
```

**Index files:** Read `website/docs/content-types.md` and identify all content types where `Index: yes`. For each such type (e.g. `posts`, `products`), run the following check — substitute the actual type name:

```bash
root="$(pwd)"
in_git=false
git -C "$root" rev-parse --git-dir >/dev/null 2>&1 && in_git=true

type=posts  # substitute actual type name from content-types.md
index="$root/website/partials/$type/index.html"

if [ ! -f "$index" ]; then
  echo "index:$type"
elif $in_git; then
  index_rel="website/partials/$type/index.html"
  last_index_commit=$(git -C "$root" log -1 --format="%H" -- "$index_rel" 2>/dev/null)
  if [ -n "$last_index_commit" ]; then
    # Any src .md committed or changed since last index commit?
    any_committed=$(git -C "$root" log --oneline "${last_index_commit}..HEAD" -- "website/src/$type/" 2>/dev/null)
    any_uncommitted=$(git -C "$root" diff HEAD -- "website/src/$type/" 2>/dev/null)
    [ -n "$any_committed" ] || [ -n "$any_uncommitted" ] && echo "index:$type"
  else
    # Index not in git — fall back to mtime
    find "$root/website/src/$type" -name "*.md" -newer "$index" 2>/dev/null | grep -q . && echo "index:$type"
  fi
else
  # Not a git repo — fall back to mtime
  find "$root/website/src/$type" -name "*.md" -newer "$index" 2>/dev/null | grep -q . && echo "index:$type"
fi
```

Run this once for each `Index: yes` type found in `content-types.md`. Substitute the actual type name before running.

---

## Step 1b — Theme-vocabulary drift (redesign)

The checks above key off `.md` staleness, so they will **not** catch a redesign — a new theme changes `components.md` while the content `.md` is unchanged. Catch it by vocabulary, not timestamps:

Read the current `website/theme/{THEME}/components.md` class list (and its `## Redesign delta` if present). For each existing `website/partials/**/*.html`, check whether every class it uses is still in that list. Any partial that references a class no longer present (renamed or dropped in the redesign) is stale-vs-theme — add it to the conversion set. Partials whose classes all still exist are left untouched — a reused vocabulary means those pages carry over for free.

Convert flagged partials per the conversion guide's "Redesign — new theme vocabulary" section (remap renamed classes, redo sections whose classes were dropped or whose paradigm changed, preserve reused structure).

---

## Step 1c — Derived-section drift (project-declared teasers)

Some projects declare, in their own `website/docs/content-types.md`, that one page embeds a bounded, reordered subset of another content type's items (e.g. a homepage teaser of showcase items) — see the conversion guide's "Derived Teaser Sections" for the declaration format (a `Feeds:` line under the source type). This is opt-in per project — most `content-types.md` files won't have one, and none of this applies when they don't.

If the current `content-types.md` has any `Feeds:` declarations: for each one, compare the source type's current item set/order (read its `.md`) against what the target page's declared section currently shows (read its partial). Any difference — items added, removed, or reordered — makes the target page stale-vs-derived-section, even though the target's own `.md` didn't change. Add it to the conversion set; regenerate only the declared section per the conversion guide, leaving the rest of the target partial untouched.

If no stale files are found (individual, index, theme-vocabulary drift, or derived-section drift): report "Nothing to sync. All layout files are up to date." and stop.

---

## Step 2 — Load Visual Context

Before converting any file, load the design references that make sync design-aware.

**2a. Conversion guide:** Read `${CLAUDE_PLUGIN_ROOT}/skills/sync-expert/references/conversion-guide.md` using the Read tool — it contains the required HTML structure, semantic class rules, index generation format, and how to use mockup HTML as a layout reference.

**2b. Chosen mockup HTML** (if available): Read `website/theme/{THEME}/mockup.html` if it exists. This is the approved visual reference — the HTML the user chose during `/b2:design`. It shows how classes compose into actual sections, not just what classes exist.

Context window note: if `website/theme/{THEME}/mockup.html` is large (more than ~250 lines), extract only the section-level structure — the outer div/section nesting and class names per section, not full content. Do not truncate; extract. Example of what to extract:

```
<section class="hero">
  <div class="hero__content"> ... </div>
  <div class="hero__mascot-panel"> ... </div>
</section>
<section class="content-block">
  <div class="content-block__inner"> ... </div>
</section>
```

If `website/theme/{THEME}/mockup.html` does not exist (design phase not yet complete), proceed without it — note this in the sync output.

---

## Step 3 — Convert Each Item

For each stale individual file, assemble a context package (Read tool) then convert.

**Context package:**
- The stale `src/{type}/page.md` — content to convert
- `website/theme/{THEME}/components.md` — available semantic classes (hard dependency)
- `website/docs/content-types.md` — layout spec for this type (match by path prefix)
- `website/docs/decisions.md` — brand voice and design language (if exists)
- **Similar existing partial** (read at most 1): use this priority order:
  1. Most recently modified existing partial of the same content type (same `src/{type}/` subfolder) — read this as a structural reference
  2. If none exists for this type, read `website/partials/index.html` (homepage partial, most representative)
  3. If neither exists, proceed without a similar-partial reference

**Get diff context (for existing partials):** If a partial already exists, run the following before converting to understand exactly what changed:

```bash
root="$(pwd)"
md_file="website/src/RELATIVE_PATH.md"    # substitute actual path
partial_file="website/partials/RELATIVE_PATH.html"

if git -C "$root" rev-parse --git-dir >/dev/null 2>&1; then
  last_commit=$(git -C "$root" log -1 --format="%H" -- "$partial_file" 2>/dev/null)
  if [ -n "$last_commit" ]; then
    echo "=== Committed changes since last sync ==="
    git -C "$root" diff "${last_commit}..HEAD" -- "$md_file"
    echo "=== Uncommitted changes ==="
    git -C "$root" diff HEAD -- "$md_file"
  else
    echo "=== Uncommitted changes (partial not in git) ==="
    git -C "$root" diff HEAD -- "$md_file"
    git -C "$root" status --short -- "$md_file"
  fi
fi
```

Use this diff output to make surgical updates — only change what actually changed in the source. If the diff is empty but the file is stale (mtime fallback), read both files and diff manually.

**Integration rule:** If a partial already exists for the file being converted, read it and integrate the content changes while preserving the HTML structure and semantic class vocabulary. Do not restore a "pristine" AI output — carry forward structural intent of any edits.

**Generation rule:** Use the mockup HTML (from Step 2b) as the compositional guide — not just isolated class names. The mockup shows how sections nest and relate. Match that structure when building new partials. Use only semantic classes from `components.md`. Do not invent class names.

**Output:** Semantic HTML fragment only — no `<html>`, `<head>`, `<body>`, header, or footer tags.

Write the output to `website/partials/{same-path-as-src}.html`, creating subdirectories as needed.

---

## Step 4 — Regenerate Stale Index Files

For each content type with `Index: yes` where any item was stale (or the index itself is missing), regenerate the index. See `${CLAUDE_PLUGIN_ROOT}/skills/sync-expert/references/conversion-guide.md` for index generation format.

**Index context package:**
- `website/docs/content-types.md` — index layout spec for this type
- `website/theme/{THEME}/components.md` — index component vocabulary
- All `website/src/{type}/*.md` files — read frontmatter from each for the listing
- `website/partials/{type}/index.html` — existing index if present (integrate)
- `website/docs/decisions.md` — brand voice (if exists)

Write to `website/partials/{type}/index.html`.

---

## Step 5 — Extend Theme (only if needed)

If a content file requires structural HTML that has no matching class in `components.md`:

1. Do NOT invent a generic or utility class name. Name it semantically for the content.
2. Read `website/theme/{THEME}/design.md` — design principles, colour system, spacing scale.
3. Write the CSS for the new component following those principles. Add it to `website/theme/{THEME}/styles.css` under the appropriate section heading (matching the existing section structure).
4. Add the new class to `website/theme/{THEME}/components.md` in the appropriate group with a usage description.
5. If the new component defines a reusable pattern (not one-off), add it to `website/theme/{THEME}/design.md` under "Component Patterns".
6. Note in the sync report: "Extended theme: added `.new-class` to styles.css + components.md"

See conversion-guide.md "Extending the Theme" section for when to extend vs. adapt.

---

## Step 6 — Update Status and Report

Update `website/docs/status.md` to mark Sync complete:

**If `website/docs/status.md` exists:** Read it. Set the Sync line to `- [x] Sync      → website/partials/`. Preserve all other lines exactly. Write the entire file back.

**If `website/docs/status.md` does not exist:** Skip this step — sync should only run after vision/brand/structure/design phases have created the file.

After updating status, output a brief summary:

```
Sync complete.

Converted:
  website/partials/posts/new-post.html (new) — used: post-header, body-text, tag-list
  website/partials/about.html (updated) — used: hero, content-block, cta

Index regenerated:
  website/partials/posts/index.html (3 posts)

Theme extended: added .quote-block to styles.css + components.md
```

List every file converted with its status (new or updated) and the semantic classes used. This confirms to the user that sync used the right components.

Then ask: "Shall I run /b2:build now to assemble dist/? (yes/no)"

If yes: use the Skill tool to invoke `b2:build-expert`.
If no: "Run /b2:build to assemble dist/ (or `make` directly if make is available)."

---

## Additional Resources

- **`${CLAUDE_PLUGIN_ROOT}/skills/sync-expert/references/conversion-guide.md`** — Detailed HTML generation rules, semantic structure, and index format
