# Structure Capability

Derive a page inventory + nav hierarchy from an existing site, formatted as a draft
`structure-expert`'s interview can start from. Never auto-written to `content-types.md` —
`structure-expert` still runs its interview, just seeded with this instead of a blank page.

## Steps

1. WebFetch the base URL's homepage. Extract the primary nav (header `<nav>` links, or the most
   prominent link list on the page).
2. WebFetch `{base}/sitemap.xml` if present; merge any same-origin URLs found there with the nav
   links (dedupe).
3. Group the resulting pages into a simple inventory:
   - **Root pages** — one-off pages (home, about, contact, pricing, ...).
   - **Recurring types** — detected by URL pattern (multiple pages sharing a path prefix, e.g.
     `/blog/{slug}` → a `post`-like type). Note the count found.
4. Write `website/docs/site-import/pages.md` (create the directory first):

```markdown
# Site Import — Page Inventory
*Source: {url}, imported {date}*

## Navigation (as found)
- Home → /
- About → /about
- ...

## Root pages
- / (home)
- /about
- /contact

## Recurring types
- blog posts (12 found): /blog/post-1, /blog/post-2, ...
```

5. Tell the user this draft exists and that `/b2:structure` will present it back for confirmation at
   the start of its interview — this capability does not run that interview itself.
