# Illustrate - Phase 2

Load and read `docs/product/illustration-style.md` before starting.

---

## Collect Context

Accept any of:
- **Text** - pasted, a file path (Read tool), or a URL (WebFetch tool)
- **Description** - "I need a hero image for the pricing page"
- **Specific scene** - "A solo founder at a whiteboard at 2am"

Read provided text fully before proposing anything. Do not skim.

---

## Analyse Before Prompting

Process internally. Output conclusions only:

1. **Core concept** - the underlying tension or idea, not just the surface topic
2. **Emotional register** - what the reader should feel on seeing this image
3. **Narrative moment** - which single frozen frame captures the essence
4. **Symbolic opportunity** - is there a metaphor that works better than a literal depiction?
5. **Composition** - aspect ratio, focal point, negative space for text overlay
6. **Fit with style brief** - how the established palette, medium, and character apply here

---

## Propose Prompts

Present **1–3 prompt concepts**. For each:

- **Concept title** - evocative, not "Option A"
- **What it shows and why** - the narrative logic
- **Aspect ratio** - `16:9` hero/banner · `1:1` square/social · `3:2` editorial · `4:5` portrait · `9:16` story
- **The full prompt** - complete, ready to copy. No blanks.

Before writing prompts, read `${CLAUDE_PLUGIN_ROOT}/skills/illustrate-expert/resources/illustration-knowledge.md`.

Do not proceed to generation without explicit approval of at least one prompt.

---

## Generate the Image

### Choose a generator

Check what is available, in this order:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/check-api-key.py"
command -v codex >/dev/null && codex features list 2>/dev/null | grep -E '^image_generation\s.*true' >/dev/null && echo CODEX_OK || echo CODEX_MISSING
```

- **Gemini key `OK`** - offer the API (Option A).
- **`CODEX_OK`** - offer the Codex CLI (Option B). Codex can attach the project's reference images, which the Gemini script cannot, so prefer Codex when the style brief relies on reference images.
- Both available - ask which to use. Neither - go to **Present the Prompt**.

Ask before generating:

> "I can generate this directly with [Gemini / Codex], or you can paste the prompt into your preferred tool. Which do you prefer?"

---

### Option A - Generate via API

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/generate.py" \
  "ASPECT_RATIO" "OUTPUT_PATH" <<'PROMPT'
FULL PROMPT TEXT HERE
PROMPT
```

Output path: `website/src/images/{page-slug}-{concept-slug}.png`, or `images/{concept-slug}.png` if no website structure.

**On `ERROR 404`:** read `${CLAUDE_PLUGIN_ROOT}/skills/image-expert/references/model-fallback.md`.
**On `ERROR 429`:** output "Rate limit hit - wait 30 seconds and retry."
**On `ERROR 4xx` (billing/auth):** fall back to **Present the Prompt** - the key may not have image generation access.

On `SAVED:` output: go to **Evaluate**.

---

### Option B - Generate via Codex CLI

Codex runs as a separate agent with an image generation tool. Write the full prompt to a file, attach every reference image with `-i`, and tell Codex exactly where to save the result.

1. Write the prompt file (outside the build folders, e.g. a scratch or `.tmp` folder). Start the prompt with:
   ```
   Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path (relative to the working directory): {MASTER_PATH}
   Do not modify any other file. When done, reply with the saved path only.

   N reference images are attached:
   1. {file} - {its role: style bible / character sheet / primary drawing-and-colour reference (style only, not content)}
   ...
   ```
   Then the approved prompt. Name each reference by file name where the prompt refers to it.
2. Run it in the background - it takes a few minutes:
   ```bash
   codex exec -s workspace-write -C "{project root}" \
     -i "{reference-1}" -i "{reference-2}" \
     - < "{prompt file}" > "{log file}" 2>&1
   ```
3. When it finishes, check that `{MASTER_PATH}` exists, then go to **Evaluate**.

**Master path:** save the PNG master outside the folder the build copies or converts (for example `docs/product/illustrations/{concept-slug}.png`), then export the web version (WebP at the displayed size, see the style brief) into the site's image folder. If the build converts every PNG in the image folder, a master saved there will overwrite a hand-tuned WebP.

**Iterating:** keep each version (`-v2`, `-v3`) and its prompt file, so the user can compare and you can reuse what worked. Put corrections from the evaluation into the prompt as explicit counter-instructions (e.g. "a previous attempt came out as one uniform brown wash; that is wrong").

**Changing details, keeping the scene:** without a reference, every run produces a new composition. When a version is close and only details must change (a character's role, an expression, a position), attach the previous version as one more `-i` image, list it in the numbered reference list, and say what to keep and what to change: "Image N is the previous version. Keep its composition, setting, colours and all text exactly; change only: ...". Update the count in "N reference images are attached" so it matches the `-i` flags.

**Expressions need size:** a small background figure reads as neutral whatever the prompt says. Put an emotion that matters on a figure that is large in the frame, or let the composition carry the point.

---

### Option C - Present the Prompt

Output the approved prompt clearly formatted for copying, then:

> "Copy this prompt into your preferred image generator:
>
> - **Midjourney** - https://www.midjourney.com
> - **ChatGPT / DALL-E 3** - https://chatgpt.com (no account needed for limited use)
> - **Ideogram** - https://ideogram.ai (free tier, excellent text rendering)
> - **Adobe Firefly** - https://firefly.adobe.com (commercially safe)
> - **Leonardo.ai** - https://app.leonardo.ai (free tier, good style control)
>
> Paste or drop the result here when ready."

---

## Evaluate

Load and follow `${CLAUDE_PLUGIN_ROOT}/skills/illustrate-expert/resources/evaluate.md`.
