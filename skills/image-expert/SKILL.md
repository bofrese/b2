---
name: image-expert
description: This skill should be used when the user explicitly runs "/b2:image" and wants to generate an image directly via the Gemini API. Requires a paid Gemini API key in .env. Do NOT trigger for general illustration requests - those are handled by /b2:illustrate.
---

# b2 Image

Generate images via the Gemini API. Free tier: 500 images/day, 2/min - no credit card required.

---

## Step 1 - Check API Key

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/check-api-key.py"
```

If output is `MISSING`: read `${CLAUDE_PLUGIN_ROOT}/skills/image-expert/references/api-key.md` and follow it. Stop here.

---

## Step 2 - Collect Inputs

| Input | Required | Default |
|-------|----------|---------|
| **prompt** | Yes | - |
| **aspect ratio** | No | `16:9` hero/banner · `1:1` square · `3:2` editorial |
| **output path** | No | `website/src/images/{kebab-slug}.png`; fall back to `./images/{kebab-slug}.png` if no `website/src/` |

---

## Step 3 - Generate

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/generate.py" \
  "ASPECT_RATIO" "OUTPUT_PATH" <<'PROMPT'
YOUR PROMPT HERE
PROMPT
```

**On `ERROR 404`:** read `${CLAUDE_PLUGIN_ROOT}/skills/image-expert/references/model-fallback.md`.

**On `ERROR 429`:** output "Rate limit hit - free tier is 2 images/min. Wait 30 seconds and retry."

**On `SAVED:` in output:** report the path and offer prompt refinement or a variation.
