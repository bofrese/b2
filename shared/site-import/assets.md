# Assets Capability

Identify and offer to download the logo and reusable content images from an existing site into
`website/src/images/`. Gated on explicit user confirmation the site is theirs.

## Steps

1. **Confirm ownership before touching anything** (this is separate from - and in addition to - 
   `trigger.md`'s Step 4 scope-guard confirmation, since Assets is the capability that actually
   writes binary files from a third party's server):
   > "Confirm this is your own site (or one you have rights to reuse assets from) - I'll only
   > download from a site you own."

   Do not proceed without an explicit yes.
2. WebFetch the homepage HTML. Identify candidates:
   - **Logo** - `<img>` with "logo" in `alt`/`class`/`id`/`src`, or `<link rel="icon">` /
     `rel="apple-touch-icon">`.
   - **Reusable content images** - `<img>` tags inside body content (not nav/footer/ad regions),
     excluding tiny icons (skip when both `width` and `height` attributes are present and under
     64px) and obvious tracking pixels (1x1, `src` containing `pixel`/`beacon`).
3. Resolve each candidate URL to an absolute URL against the base URL.
4. List candidates to the user (logo separately from content images) and ask which to download.
   Default: logo + all content images found, capped at 10 - if more than 10 candidates exist, ask
   before downloading beyond the cap.
5. Download confirmed assets (Bash tool):
   ```bash
   mkdir -p website/src/images
   curl -sL -o website/src/images/{filename} {url}
   ```
   Keep the original filename where it's sane (lowercase, no query string); sanitise otherwise
   (lowercase, hyphens, strip query params).
6. Report what was downloaded and where. Note these are available media, not automatically wired
   into any page - `/b2:write` and `/b2:design` reference them by filename when relevant.
