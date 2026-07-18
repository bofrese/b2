# Illustrate — Phase 2

Load and read `docs/product/illustration-style.md` before starting.

---

## Collect Context

Accept any of:
- **Text** — pasted, a file path (Read tool), or a URL (WebFetch tool)
- **Description** — "I need a hero image for the pricing page"
- **Specific scene** — "A solo founder at a whiteboard at 2am"

Read provided text fully before proposing anything. Do not skim.

---

## Analyse Before Prompting

Process internally. Output conclusions only:

1. **Core concept** — the underlying tension or idea, not just the surface topic
2. **Emotional register** — what the reader should feel on seeing this image
3. **Narrative moment** — which single frozen frame captures the essence
4. **Symbolic opportunity** — is there a metaphor that works better than a literal depiction?
5. **Composition** — aspect ratio, focal point, negative space for text overlay
6. **Fit with style brief** — how the established palette, medium, and character apply here

---

## Propose Prompts

Present **1–3 prompt concepts**. For each:

- **Concept title** — evocative, not "Option A"
- **What it shows and why** — the narrative logic
- **Aspect ratio** — `16:9` hero/banner · `1:1` square/social · `3:2` editorial · `4:5` portrait · `9:16` story
- **The full prompt** — complete, ready to copy. No blanks.

Before writing prompts, read `${CLAUDE_PLUGIN_ROOT}/skills/illustrate-expert/resources/illustration-knowledge.md`.

Do not proceed to generation without explicit approval of at least one prompt.

---

## Generate the Image

### Check for API key

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/check-api-key.py"
```

**If `OK`** — a Gemini API key is available. Ask:

> "I found an API key — shall I generate this directly, or would you rather paste the prompt into your preferred tool?"

- **API:** run `generate.py` (see below), then go to **Evaluate**
- **External tool:** go to **Present the Prompt**

**If `MISSING`** — go straight to **Present the Prompt**

---

### Option A — Generate via API

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/generate.py" \
  "ASPECT_RATIO" "OUTPUT_PATH" <<'PROMPT'
FULL PROMPT TEXT HERE
PROMPT
```

Output path: `website/src/images/{page-slug}-{concept-slug}.png`, or `images/{concept-slug}.png` if no website structure.

**On `ERROR 404`:** read `${CLAUDE_PLUGIN_ROOT}/skills/image-expert/references/model-fallback.md`.
**On `ERROR 429`:** output "Rate limit hit — wait 30 seconds and retry."
**On `ERROR 4xx` (billing/auth):** fall back to **Present the Prompt** — the key may not have image generation access.

On `SAVED:` output: go to **Evaluate**.

---

### Option B — Present the Prompt

Output the approved prompt clearly formatted for copying, then:

> "Copy this prompt into your preferred image generator:
>
> - **Midjourney** — https://www.midjourney.com
> - **ChatGPT / DALL-E 3** — https://chatgpt.com (no account needed for limited use)
> - **Ideogram** — https://ideogram.ai (free tier, excellent text rendering)
> - **Adobe Firefly** — https://firefly.adobe.com (commercially safe)
> - **Leonardo.ai** — https://app.leonardo.ai (free tier, good style control)
>
> Paste or drop the result here when ready."

---

## Evaluate

Load and follow `${CLAUDE_PLUGIN_ROOT}/skills/illustrate-expert/resources/evaluate.md`.
