# Design Capability

Screenshot key pages of an existing site and extract a short look/feel brief, formatted to seed
`design-expert`'s interview opening ("here's your current look - what do you like, what doesn't
work?").

## Playwright detection - reuse, do not reimplement

Use the exact same detection order as `website-review-expert` (`b2/skills/website-review-expert/SKILL.md`
Step 3):

1. **MCP browser tools** - if `browser_navigate` / `browser_take_screenshot` are available in this
   session, use them directly.
2. **npx playwright** - `npx playwright --version 2>/dev/null || echo "not found"`; if found:
   `npx playwright screenshot {url} {path}`.
3. **playwright CLI** - `playwright --version 2>/dev/null || echo "not found"`; if found:
   `playwright screenshot {url} {path}`.
4. **None available** - halt this capability only (Content/Structure/Assets are unaffected):
   > "Playwright not found. Install it with `npx playwright install`, or add the Playwright MCP
   > plugin to Claude Code. Then re-run the design import."

## Steps

1. Pick up to 5 key pages: homepage + up to 4 more. Reuse `website/docs/site-import/pages.md` if the
   Structure capability already ran this session; otherwise use the homepage nav directly.
2. `mkdir -p .playwright-mcp/site-import`, then screenshot each page to
   `.playwright-mcp/site-import/{slug}.png`.
3. From the homepage HTML (WebFetch, reuse if already fetched), note: dominant colours (CSS custom
   properties, prominent hex/rgb values in inline `<style>` or a linked stylesheet if fetchable),
   font-family declarations, and layout observations drawn from the screenshots (hero style, spacing
   density, card/grid use, dominant imagery vs. text-heavy).
4. Write `website/docs/site-import/design-brief.md` (create the directory first):

```markdown
# Site Import - Look/Feel Brief
*Source: {url}, imported {date}*

## Colour impression
[2-3 sentences + any hex values found]

## Typography impression
[serif/sans, weight, any font names found]

## Layout patterns
[hero style, spacing, grid/card use, notable structural choices]

## Screenshots
- .playwright-mcp/site-import/{slug}.png (one per page reviewed)
```

5. Tell the user this brief exists and that `/b2:design` will open its aesthetic interview with it - 
   this capability does not run that interview itself, and does not decide whether the existing look
   is kept; that's the user's call during the design interview.
