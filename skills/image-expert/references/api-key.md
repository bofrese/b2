# Gemini API Key - Setup Guide

Load this reference only when `check-api-key.py` returns `MISSING`.

---

## Output This Message

> **GEMINI_API_KEY not found.**
>
> A free Google AI Studio key is required (no credit card, 500 images/day).
>
> **Step 1 - Get the key:**
> Open https://aistudio.google.com/apikey, sign in with a Google account, create an API key, and copy it.
>
> **Step 2 - Save it (choose one):**
>
> **Option A - `.env` file** (project-specific, not committed to git):
> Create or open `.env` in the project root and add:
> ```
> GEMINI_API_KEY=your_key_here
> ```
> Make sure `.env` is in your `.gitignore` (it usually is by default).
>
> **Option B - Environment variable** (global, works across all projects):
> Add to `~/.zshrc` or `~/.bashrc`:
> ```
> export GEMINI_API_KEY=your_key_here
> ```
> Then run `source ~/.zshrc` or open a new terminal.
>
> Paste the key here and choose an option, or run `/b2:image` again once saved.

---

## If the User Pastes the Key

To save to `.env`:

1. Check whether `.env` exists at the project root
2. If it exists: read it, replace any existing `GEMINI_API_KEY=` line, write back
3. If it doesn't exist: create it with the single line `GEMINI_API_KEY=your_key_here`
4. Confirm: "Key saved to `.env`. Ready to generate."

Note: if `.env` is not already in `.gitignore`, suggest adding it:
```
echo '.env' >> .gitignore
```
