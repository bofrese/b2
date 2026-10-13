# Evaluate - Image Review and Iteration

This phase runs after the user provides an image - whether from the API or an external tool.

Track the session state in context (not written to disk):
- the original approved prompt
- the intended use and concept
- the current iteration number
- what changed between iterations and why

---

## Collect the Image

If the image has not yet been provided, prompt:

> "Drop the image into the chat, or give me the file path."

Accept:
- **File path** - read with the Read tool (Claude supports PNG, JPG, WebP)
- **Pasted image** - Claude can see images pasted directly into the conversation

---

## Evaluate Against Three Criteria

Assess the image honestly against all three. Be specific - name exactly what works and what doesn't.

### 1. Style Match
Compare against `docs/product/illustration-style.md`:
- Medium and rendering - does it match (flat vector, gouache, risograph, etc.)?
- Colour palette - does it use the right hues and register (muted, warm, saturated)?
- Line quality - weight and character consistent with the brief?
- Texture and finish - grain, halftone, smoothness as specified?
- Mood - does the emotional register match?

### 2. Compositional Fit
Assess against the intended use:
- **Hero/banner (16:9):** breathing room for text overlay, subject offset to one third
- **Article header (3:2):** readable at thumbnail size (100px), strong focal point
- **Spot illustration (1:1):** one clear subject, works small
- **Social/portrait (4:5, 9:16):** vertical energy, subject fills frame

Is the aspect ratio right? Is there enough negative space where needed?

### 3. Concept and Story
- Does the image communicate the intended idea at a glance?
- Is the metaphor landing, or is it too literal / too obscure?
- Does it feel like it belongs to this site, or could it be from anywhere?

---

## Output the Verdict

Give a direct assessment. No softening. Examples:

> **Style: ✓ Palette and texture are right - the grain and muted greens match the brief exactly.**
> **Composition: ✗ The subject is centred - there's no space for a headline. This won't work as a hero.**
> **Concept: ✓ The metaphor is strong. The figure and the mountain of paper is immediately readable.**
>
> **Verdict: Needs revision - composition is the blocker.**

Or if genuinely good:

> **All three criteria met. This is a strong illustration - ready to use.**

Then ask the user:

> "Happy with this, or shall we push it further?"

---

## Iterate

If the image needs revision - either because the user isn't satisfied, or because the evaluation found real problems:

1. Diagnose the specific failure(s) from the evaluation
2. Construct an improved prompt that directly addresses them
3. Explain what changed and why - do not just produce a new prompt without reasoning
4. Present the revised prompt using the same format as the original proposal
5. Return to **Generate the Image** in `illustrate.md`

Iteration limit: there is none - keep going until the user approves or gives up. But if the same problems recur after two iterations, name the pattern:

> "We've hit the same composition problem twice. This may be a style brief constraint - the brief's flat graphic style naturally centres subjects. Want to try a different approach, or revisit the style?"

---

## Background Removal (if needed)

After the user approves an image, check whether the intended use requires a transparent background.

**Transparent background is typically needed for:**
- Spot illustrations placed over a coloured section or gradient
- Icons or decorative elements composited into a layout
- Images where the design brief specifies transparency

**Not needed for:**
- Hero/banner images (full-bleed, opaque background is correct)
- Article header images (rectangular crop, no transparency)

If the use case suggests transparency, ask:

> "Does this need a transparent background? Spot illustrations often do when they're placed over a coloured section."

If yes, run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/remove-bg.py" \
  "INPUT_PATH" "OUTPUT_PATH"
```

Output path: if not specified, defaults to `{original-stem}-nobg.png` alongside the source file.

**If output is `NOT_INSTALLED`:**

> "`rembg` is not installed. To enable background removal:
> ```
> pip install rembg
> ```
> The first run downloads a ~180MB AI model. After that it works offline. Re-run `/b2:illustrate` once installed."

**On `SAVED:`:** report the path. The transparent PNG is ready to use.

---

## End of Session

When the user approves an image, assess the session:

**If the first approved image matched the original prompt without significant changes:**
Log the result and finish:

```bash
# Append to website/docs/illustrations.md
```

```markdown
## YYYY-MM-DD - [Page or context]

| File | Concept | Prompt |
|------|---------|--------|
| `website/src/images/foo.png` | [title] | "[first 100 chars]..." |
```

**If iteration was needed, or if the final image diverged from the style brief on any dimension:**

Always ask:

> "The final image differed from the style brief on [specific dimensions - e.g. 'palette was warmer than specified, and we dropped the grain texture']. Should I update `docs/product/illustration-style.md` to reflect what actually worked? This will keep future illustrations consistent with this one."

If yes: read the current `docs/product/illustration-style.md`, identify the specific fields that need updating based on what the approved image actually looked like, and propose the exact changes before writing. Do not rewrite the whole document - update only what changed.

Then log and finish as above.
