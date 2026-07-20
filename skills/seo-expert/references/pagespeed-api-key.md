# PageSpeed Insights API Key — Setup Guide

Load this reference only when `scripts/check-pagespeed-key.py` returns `MISSING`.

The API works without a key, but on a small shared quota — a global bucket every unauthenticated caller draws from, so it is frequently already exhausted regardless of who's asking. A free key removes this.

---

## Output This Message

> **No PageSpeed API key found — and the free unauthenticated quota is often already exhausted by other traffic.**
>
> A free Google Cloud API key removes this (no billing required for this specific API).
>
> **Step 1 — Get the key:**
> 1. Open https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com
> 2. Select or create a project, then click **Enable**
> 3. Go to **APIs & Services → Credentials → Create Credentials → API Key**
> 4. Copy the key
>
> **Step 2 — Save it (choose one):**
>
> **Option A — `.env` file** (project-specific, not committed to git):
> Create or open `.env` in the project root and add:
> ```
> GOOGLE_PAGESPEED_API_KEY=your_key_here
> ```
> Make sure `.env` is in your `.gitignore` (add it if not).
>
> **Option B — Environment variable** (global, works across all projects):
> Add to `~/.zshrc` or `~/.bashrc`:
> ```
> export GOOGLE_PAGESPEED_API_KEY=your_key_here
> ```
> Then run `source ~/.zshrc` or open a new terminal.
>
> Paste the key here and I'll save it, or run `/b2:seo` again once saved.

---

## If the User Pastes the Key

Save to `.env` — never to `b2.cfg` or any other tracked file, since this key should not be committed:

1. Check whether `.gitignore` already excludes `.env`. If not, append it: `echo '.env' >> .gitignore`
2. Check whether `.env` exists at the project root
3. If it exists: read it, replace any existing `GOOGLE_PAGESPEED_API_KEY=` line, write back
4. If it doesn't exist: create it with the single line `GOOGLE_PAGESPEED_API_KEY=your_key_here`
5. Confirm: "Key saved to `.env`. Running the PageSpeed check now."
