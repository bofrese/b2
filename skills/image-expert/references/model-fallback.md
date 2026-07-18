# Model Fallback

Load this reference only when `generate.py` exits with an HTTP 404 error.

---

## Find Available Image Models

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/find-models.py"
```

Output is one model ID per line, without the `models/` prefix, ready to pass directly to `generate.py`.

Prefer `flash` over `pro` for free-tier use. Avoid `ultra`.

---

## Retry with New Model ID

Pass the model ID as the third argument:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/image-expert/scripts/generate.py" \
  "ASPECT_RATIO" "OUTPUT_PATH" "new-model-id-here" <<'PROMPT'
...prompt...
PROMPT
```

---

## If No Image Models Found

The free tier may have changed. Check current models and pricing at:
https://ai.google.dev/gemini-api/docs/models

Report which models are available and whether any offer a free tier.
