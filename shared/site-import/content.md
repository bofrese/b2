# Content Capability

Fetch page text from an existing site and produce draft `website/src/{slug}.md` files matching
`write-expert/references/create.md`'s frontmatter conventions.

## Steps

1. WebFetch the base URL's homepage.
2. Extract internal links (same-origin; ignore `#fragments`, `mailto:`, `tel:`, external domains)
   from the nav and body — this is the candidate page list. Cap at 15 pages; if more are found, list
   them and ask the user which to prioritise rather than importing all of them.
3. For each page URL: WebFetch it, extract readable body text (headings, paragraphs, lists) —
   discard nav, footer, cookie banners, and script/style content. If a page's fetched text is
   near-empty (likely JS-rendered), skip it and note it in the report — point at the Design
   capability's Playwright path (`design.md`) as a manual fallback for that page rather than
   building a second fetch strategy here.
4. Derive a slug from the URL path: homepage → `index`; `/about` → `about`; a page under a repeating
   path like `/blog/post-1` → `posts/post-1` (treat as the typed-content convention
   `write-expert`/`structure-expert` already use).
5. Write `website/src/{slug}.md` (create `website/src/` first if missing) using minimal frontmatter
   matching `write-expert/references/create.md` Step 4's fallback (`title`, `description` for pages —
   swap to the type's real spec later once `content-types.md` exists). Body: the extracted text,
   lightly cleaned (strip obvious boilerplate, keep heading/paragraph/list structure) — do NOT
   rewrite it into finished copy. This is a raw import draft, not a copy edit.
6. Prepend an HTML comment marking the file as an import draft:
   `<!-- Imported from {url} on {date}. Run /b2:write to refine. -->`
7. **Never overwrite an existing `website/src/{slug}.md` without confirming per-file** — an import
   draft must not silently clobber real work already written for that slug.
8. Report: pages imported (path written), pages skipped (and why — JS-rendered, fetch error,
   duplicate slug declined).
