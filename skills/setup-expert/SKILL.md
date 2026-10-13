---
name: setup-expert
description: This skill should be used when the user runs "/b2:setup", asks to "set up the build", "configure the build", "verify the setup", or "run setup". Detects the build platform, asks about hosting, writes b2.cfg, ensures required folders exist, and runs the first build.
---

# b2 Setup Expert

Configure the b2 build environment and run the first build. This is the final setup step - run it after `/b2:sync` has converted your content files.

---

## Prerequisite Check

Read `website/b2.cfg` if it exists. Look for a `THEME=` line. Default: `THEME=b2`. Theme directory: `website/theme/{THEME}/`.

Read `website/theme/{THEME}/components.md` using the Read tool. If missing, stop:

> "Run `/b2:design` first - setup requires a completed theme with components.md."

Read `website/docs/status.md` if it exists. If there is no `[x] Sync` line, warn:

> "No sync has been run yet. Run `/b2:sync` first to convert your .md files to HTML partials, or partials may be missing and the build may fail."

Proceed regardless - the user may want to configure b2.cfg before syncing.

---

## Step 1 - Detect Build Tool

Check whether a `website/Makefile` exists first (Bash tool):

```bash
[ -f "$(pwd)/website/Makefile" ] && echo "makefile found" || echo "makefile not found"
```

- If `website/Makefile` exists: `BUILD_TOOL=make`
- If not: `BUILD_TOOL=scripts` - build-expert will use its bundled assembly scripts

Do **not** check for the `make` binary. A Makefile that doesn't exist can't be run even if `make` is installed, and the scripts fallback works everywhere.

---

## Step 2 - Hosting Configuration

Ask the user:

> "Will this site live at a root domain (e.g., `example.com/`) or at a subdirectory (e.g., GitHub Pages `example.com/project-name/`)?
>
> 1. Root domain - no base path needed
> 2. Subdirectory - enter the path (e.g., `/project-name`)"

- If root domain: `BASE_PATH=/`
- If subdirectory: `BASE_PATH=/their-path`

Note: if `BASE_PATH` is not `/`, setup will patch all absolute nav hrefs in `header.html` and `footer.html` - see Step 3b below.

---

## Step 2b - Site URL

Ask the user: "What's the live URL for this site? (e.g., `https://example.com`, no trailing slash) Leave blank if you don't know it yet - you can add it later."

Store the answer as `SITE_URL=` (empty string if skipped). This is what the build injects into canonical URLs, `og:url`, and the sitemap - every page needs it, not just the SEO pass.

---

## Step 3 - Update b2.cfg

Read `website/b2.cfg`. It should already exist and contain a `THEME=` line written by `/b2:design`. Add or update only `BUILD_TOOL`, `BASE_PATH`, and `SITE_URL` - do not change the `THEME=` line.

Write the complete file preserving all existing keys:

```
THEME={value from existing b2.cfg}
BUILD_TOOL={make|scripts}
BASE_PATH={/|/subpath}
SITE_URL={https://example.com|empty}
```

**If `website/b2.cfg` does not exist** (design was skipped or b2.cfg was deleted): write the full file with `THEME=b2` as fallback, and warn the user: "b2.cfg was missing - created with THEME=b2. If your theme folder has a different name, update THEME in website/b2.cfg."

---

## Step 3b - Patch Nav Links for Subdirectory BASE_PATH

If `BASE_PATH` is `/`, skip this step.

If `BASE_PATH` is anything else (e.g., `/mysite`), prefix all absolute nav hrefs in `header.html` and `footer.html` (Bash tool):

```bash
THEME=$(grep '^THEME=' website/b2.cfg | cut -d= -f2 | tr -d '[:space:]')
BASE_PATH=$(grep '^BASE_PATH=' website/b2.cfg | cut -d= -f2 | tr -d '[:space:]')
HEADER="website/theme/$THEME/header.html"
FOOTER="website/theme/$THEME/footer.html"
# Prefix href="/ and src="/ with BASE_PATH (macOS sed requires backup extension)
sed -i.bak "s|href=\"/|href=\"$BASE_PATH/|g" "$HEADER"
sed -i.bak "s|href=\"$BASE_PATH//\"|href=\"$BASE_PATH\"|g" "$HEADER"
sed -i.bak "s|src=\"/|src=\"$BASE_PATH/|g" "$HEADER"
sed -i.bak "s|href=\"/|href=\"$BASE_PATH/|g" "$FOOTER"
sed -i.bak "s|src=\"/|src=\"$BASE_PATH/|g" "$FOOTER"
rm -f "website/theme/$THEME"/*.bak
```

**Constraint:** Changing BASE_PATH later requires re-running `/b2:setup`. Changing the theme (via `/b2:design`) after setup requires re-running `/b2:setup` to reapply BASE_PATH.

---

## Step 4 - Verify Required Folders

Create any missing directories (Bash tool):

```bash
mkdir -p website/src website/partials website/docs
```

Do not create `website/dist/` - the build tool handles that.

---

## Step 4b - Cache-Control Policy

If `website/src/.htaccess` does not already exist, write it (Write tool):

```apache
# Cache policy - pairs with the ?v={hash} cache-busting query param the build
# adds to /styles.css and /scripts.js: those two are safe to cache long-term
# because their URL changes whenever their content does. HTML must always
# revalidate since its URL never changes between deploys.
<IfModule mod_headers.c>
  <FilesMatch "\.html$">
    Header set Cache-Control "no-cache, must-revalidate"
  </FilesMatch>
  <FilesMatch "\.(css|js)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\.(woff2?|jpe?g|png|webp|gif|svg|ico)$">
    Header set Cache-Control "public, max-age=2592000"
  </FilesMatch>
</IfModule>
```

It's a dotfile under `website/src/`, so both build paths (`make` and the scripts fallback) copy it to `dist/.htaccess` automatically, same as any other non-`.md` asset - no separate wiring needed. Apache-only (the documented/tested host target); harmless if the eventual host isn't Apache - an unrecognized `.htaccess` is just ignored, not an error. If the file already exists (user customized it, or setup is re-running), leave it untouched.

---

## Step 5 - Run First Build

**If BUILD_TOOL=make:**

```bash
cd website && make
```

If `make` succeeds: record success.
If `make` fails: show the error output, diagnose the root cause (missing files, stale .md with no partial, syntax error), suggest the specific fix. Do NOT auto-fix Makefile issues.

**If BUILD_TOOL=scripts:**

Inform the user: "No Makefile found - the first build will be run by `/b2:build` using the built-in assembly scripts. Run `/b2:build` next."

Skip the actual build step.

---

## Step 6 - Update Status and Report

Update `website/docs/status.md` - mark Setup complete:

**If `website/docs/status.md` exists:** Read it. Set the Setup line to `- [x] Setup     → website/b2.cfg`. Preserve all other lines. Write the file back.

**If `website/docs/status.md` does not exist:** Skip (the file should already exist from previous phases).

**Report on success:**

```
Setup complete.

  website/b2.cfg     ✓  (THEME=b2, BUILD_TOOL={tool}, BASE_PATH={path})
  website/src/       ✓
  website/partials/  ✓
  website/docs/      ✓
  .htaccess          ✓  (cache-control policy)    ← if newly written this run
  make               ✓  (built N files)    ← if BUILD_TOOL=make and make ran

Run /b2:serve to preview your site in the browser.
```

**If BASE_PATH is not /**, add:

```
⚠ Subdirectory base path: nav links in website/theme/{THEME}/header.html have been prefixed with {BASE_PATH}.
  If you later change BASE_PATH or regenerate the theme, re-run /b2:setup.
```
