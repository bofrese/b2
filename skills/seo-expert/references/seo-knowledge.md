# Elite SEO Knowledge Reference

This file is the SEO knowledge base for the b2 seo-expert skill. Load it when executing audits, coaching users, or answering SEO questions. Prioritise actionable, high-leverage advice over exhaustive checklists.

---

## Mental Model: What Google Actually Optimises For

Google's core algorithm goal is to surface the page that best satisfies a searcher's intent while being trustworthy, fast, and accessible. All ranking signals are proxies for this goal. Tactics that game proxies without improving the underlying reality tend to work short-term and fail on major updates (Panda, Penguin, Helpful Content, Core). The durable strategy: build the genuinely best page for the query.

---

## Priority Stack — Ranked by Leverage

Work this stack top-to-bottom. Don't optimise copy before fixing indexation. Don't build backlinks before fixing technical.

### 1. Crawlability and Indexation (foundation)
Nothing else matters if Google can't crawl and index the page.

- **robots.txt** — must not accidentally block `/`. Test at `yourdomain.com/robots.txt`.
- **sitemap.xml** — must exist, be submitted to Google Search Console, and cover all canonical pages.
- **Canonical tags** — every page needs `<link rel="canonical" href="...">`. Prevents duplicate content penalties from www/non-www, trailing slash variations, and URL parameters.
- **noindex audit** — check no pages accidentally carry `<meta name="robots" content="noindex">`.
- **HTTPS** — required. Mixed content (HTTP assets on HTTPS page) triggers browser warnings and ranking penalties.
- **404 handling** — broken internal links waste crawl budget and signal poor site health.

### 2. Core Web Vitals (technical performance)
Google uses CWV as a ranking tiebreaker. On competitive SERPs, poor CWV loses.

- **LCP (Largest Contentful Paint)** — target < 2.5s. Common culprits: unoptimised hero image, render-blocking CSS/JS, slow server.
- **CLS (Cumulative Layout Shift)** — target < 0.1. Common culprit: images without `width`/`height` attributes, late-loading fonts.
- **INP (Interaction to Next Paint)** — target < 200ms. Replaced FID in 2024. Common culprit: heavy JavaScript on main thread. Static sites built by b2 typically score well here.

Tools: Google PageSpeed Insights (free), Chrome DevTools Lighthouse, Search Console CWV report.

### 3. On-Page Signals

**Title tag** (most important on-page signal):
- 50–60 characters. Over 60 gets truncated in SERPs.
- Primary keyword first or second word. Don't bury it at the end.
- Every page needs a unique title.
- Treat it as ad copy — it drives click-through rate, which is a feedback ranking signal.

**Meta description** (drives CTR, not a ranking signal):
- 150–160 characters. Google rewrites ~70% of them, but a good one still improves CTR.
- Include the primary keyword (Google bolds matches in SERPs).
- Write a compelling reason to click — don't just describe, sell the click.

**H1**:
- One per page. Contains the primary keyword.
- Different from the title tag is fine (often better — H1 can be more editorial, title tag more SERP-optimised).

**Heading hierarchy**:
- H1 → H2 → H3 without skipping levels.
- H2s should cover the main subtopics a user searching the query would expect.

**Content depth**:
- Google's quality rater guidelines use E-E-A-T: Experience, Expertise, Authoritativeness, Trust.
- For competitive queries: study the top 3 pages. Your content needs to be as comprehensive, or more so, with genuinely better information.
- Minimum viable: 300 words. Competitive: 800–2,000+ depending on topic complexity.

**Keyword placement**:
- Keyword in title, H1, first 100 words, at least one H2, meta description.
- Natural usage — do not stuff. Semantic synonyms and related terms are as valuable as exact match.

**Image optimisation**:
- Descriptive file names: `seo-audit-checklist.jpg` beats `IMG_4821.jpg`.
- Alt text on every meaningful image. Describe what it shows, include keyword if natural.
- WebP format. Lazy loading (`loading="lazy"` on below-fold images).
- `width` and `height` attributes to prevent CLS.

**Internal linking**:
- Every page should be reachable via internal links — no orphan pages.
- Use descriptive anchor text with target keyword (not "click here").
- Your highest-authority pages (most backlinks) should link to the pages you most want to rank.
- This distributes PageRank where you need it most.

**URL structure**:
- Clean, lowercase, hyphens not underscores.
- Include primary keyword.
- Short is better: `/seo-audit/` beats `/blog/2024/march/how-to-do-an-seo-audit-for-beginners/`.

### 4. Semantic HTML and Accessibility
These overlap significantly with SEO. Google's crawler reads HTML like a screen reader.

- Semantic landmarks: `<main>`, `<nav>`, `<header>`, `<footer>`, `<article>`, `<section>`.
- `lang` attribute on `<html>` — required for language detection.
- `viewport` meta tag — required for mobile-first indexing.
- Focus states visible. Links have descriptive text.

### 5. Structured Data (Schema Markup)
JSON-LD structured data helps Google understand page content beyond keywords. It powers rich results (star ratings, FAQ dropdowns, sitelinks search box) which dramatically improve CTR.

High-value schema types:
- `Organization` — for the business/site itself. Include `sameAs` pointing to social profiles, Wikipedia, Crunchbase, etc. This establishes your entity in Google's Knowledge Graph.
- `WebSite` — enables sitelinks search box.
- `WebPage` / `Article` / `BlogPosting` — for content pages.
- `FAQPage` — for FAQ sections. Generates expandable dropdown in SERPs.
- `HowTo` — for step-by-step guides.
- `BreadcrumbList` — for navigational context.
- `Product` + `AggregateRating` — if selling anything.

All schema should be in `<script type="application/ld+json">` blocks in `<head>`. Validate at schema.org/validator or Google's Rich Results Test.

### 6. Open Graph and Social Tags
Not a direct ranking signal but controls how pages appear when shared. Social traffic can drive backlinks which do affect ranking.

Minimum required:
```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="..."> <!-- 1200x630px recommended -->
<meta property="og:url" content="...">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

### 7. Topical Authority (content strategy)

The single biggest gap between average and elite SEO: authority is built at the **topic** level, not the page level.

**Pillar + Cluster model**:
- Pillar page: broad, authoritative overview of the topic (~2,000+ words).
- Cluster pages: specific sub-topics, all internally linking back to the pillar.
- Result: Google understands your site *owns* the topic.

**Content freshness**:
- For evergreen content: update top-performing pages every 6–12 months.
- Updating existing pages preserves their link equity (unlike publishing new pages).
- Change the `lastmod` date, add new data, improve depth.
- Query Deserves Freshness (QDF) algorithm rewards recency on trending/news queries.

**Thin pages drag down the whole domain**:
- Post-Helpful Content update (2023), Google evaluates quality at site level.
- A handful of thin, low-value pages can suppress rankings for your good pages.
- Audit and either improve thin pages or set them to noindex.

### 8. Featured Snippets (Position Zero)
Featured snippets appear above organic results and capture ~35% of clicks.

To win snippets:
- Ask the exact question as an H2 heading.
- Answer it in 40–60 words directly below the heading.
- For list snippets: use `<ul>` or `<ol>` with 8+ items (Google truncates and shows "more items" — a CTR increase).
- For table snippets: use proper `<table>` markup.
- Must already rank on page 1 for the query — snippets are not a shortcut to ranking.

### 9. Entity SEO (advanced)
Google's Knowledge Graph understands entities (people, companies, products, places) and their relationships — not just keywords. A site associated with a known entity ranks with more confidence.

How to establish entity presence:
- Consistent name/business details everywhere Google scrapes.
- `sameAs` in `Organization` schema pointing to: LinkedIn, Crunchbase, Wikipedia, industry databases.
- Google Business Profile (for local businesses).
- Author pages with verifiable credentials.
- Wikipedia / Wikidata presence if achievable.

Payoff: Google begins surfacing your site for queries it hasn't explicitly optimized for, because it understands what your entity *is about*.

### 10. Backlinks (off-page authority)
Still the strongest ranking signal. Cannot be faked sustainably.

Quality over quantity:
- One link from a relevant, authoritative source in your niche beats 100 from directories.
- Links from pages that themselves rank for your target keywords are disproportionately valuable.
- Anchor text diversity — over-optimised anchor text (all exact match) is a Penguin penalty signal.

Link acquisition strategies (white-hat):
- Original research / data that others cite.
- Tools and resources (calculators, templates, guides) that attract natural links.
- Guest posts on relevant industry sites.
- HARO (Help a Reporter Out) — earn media links.
- Broken link building — find broken links on relevant sites, offer your page as replacement.

### 11. CTR Optimisation (SERP click-through)
Google uses CTR as a ranking feedback signal. A page that outperforms its position's expected CTR will be promoted.

Title tag tactics that improve CTR:
- Numbers: "7 ways..." consistently outperforms "Ways to..."
- Current year for competitive evergreen queries.
- Brackets: `[Guide]`, `[2026]`, `[Template]`, `[Free Tool]`.
- Power words: "exact", "proven", "fastest", "complete", "ultimate".
- Questions when the query is a question.

Meta description tactics:
- Include a clear benefit or outcome.
- Match the emotional tone of the search intent.
- Use numbers and specifics.

### 12. Technical Deep Cuts (for advanced audits)

**Log file analysis** — your server logs show exactly what Googlebot crawls, how often, and where it wastes budget. Most SEOs never do this. Reveals: pages crawled repeatedly but not ranking (quality signal issue), pages never crawled (internal link problem), crawl budget wasted on filter/parameter URLs.

**Crawl budget management** — large sites: block low-value URLs (search filters, session parameters, duplicate listing variants) in robots.txt or via canonical.

**Redirect chains** — A→B→C wastes crawl budget and dilutes link equity. Flatten to direct redirects.

**Hreflang** — for multilingual sites. Signals to Google which page to show for which language/region. Common mistake: hreflang tags that don't reference each other (must be bidirectional).

**Pagination** — for paginated series, use `rel=next`/`rel=prev` or canonical to index page to handle duplicate content.

**JavaScript SEO** — if content is rendered client-side by JavaScript, Google may not index it. Use server-side rendering (SSR) or static generation for SEO-critical content. b2 generates static HTML — no JS rendering issues.

---

## What Not To Do

- **Keyword stuffing** — penalised. Natural language with semantic variation is what works.
- **Buying links** — manual penalty risk. Not worth it.
- **Duplicate content** — dilutes authority. Canonical everything that might duplicate.
- **Thin affiliate pages** — Google's Helpful Content updates specifically target these.
- **Cloaking** — showing different content to Googlebot than to users. Permanent penalty risk.
- **Hidden text** — same font colour as background, 0px text, etc. Detected and penalised.
- **Private Blog Networks (PBNs)** — link schemes. Risk vs. reward not worth it.
- **Exact-match anchor text at scale** — over-optimised. Use branded + natural + keyword mix.

---

## Measurement: What to Track

**Google Search Console** (free, essential):
- Index Coverage — crawl errors, excluded pages.
- Core Web Vitals — real-user data.
- Performance — clicks, impressions, CTR, average position by query and page.
- Rich Results — schema validation and coverage.

**Google Analytics 4** (free):
- Organic traffic channel, landing pages, conversion rates.

**Rank tracking** (paid tools — Ahrefs, Semrush, Moz — or free Ubersuggest):
- Track target keywords weekly.
- Monitor competitor movement.

**Backlink monitoring** (Ahrefs/Semrush):
- New backlinks, lost backlinks, toxic links.

**PageSpeed Insights** (free):
- CWV scores by page.
- Specific improvement recommendations.

---

## The Meta-Insight

The sites that dominate SERPs long-term are not the most technically optimised — they are the ones that most reliably satisfy users. Every major algorithm update (Panda, Penguin, Helpful Content, Core Updates) has hurt sites gaming proxies and helped sites genuinely useful to searchers. Optimise for the user. Instrument it with the tools above. Google follows.
