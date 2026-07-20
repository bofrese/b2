#!/usr/bin/env python3
"""
pagespeed-check.py — Call the Google PageSpeed Insights API and report a
focused, machine-parsable summary of Core Web Vitals and top opportunities.

No browser automation, no Chrome extension dependency — just the public
REST API (stdlib urllib only). Works headlessly in any environment.

Usage:
  python3 pagespeed-check.py <url> [--strategy mobile|desktop] [--categories performance,accessibility,best-practices,seo]

  URL must be the LIVE, published URL — PageSpeed cannot see localhost or
  unpublished dist/ files. The caller is responsible for confirming with the
  user that the current build has been published before running this.

Auth:
  Works without a key (small shared quota — often already exhausted, since
  it's a global bucket shared by every unauthenticated caller, not per-IP).
  A free key removes this: enable the PageSpeed Insights API in Google Cloud
  Console and create an API key (no billing required for this API). Read
  from, in order: GOOGLE_PAGESPEED_API_KEY / PAGESPEED_API_KEY in `.env`
  (project root), then the same names as real environment variables.
  See references/pagespeed-api-key.md for the guided setup flow.

Output format (stable, prefix-based — parse by leading token):
  STRATEGY:{mobile|desktop}
  SCORE:{category}:{0-100}
  METRIC:{name}:{value}:{GOOD|NEEDS_IMPROVEMENT|POOR}
  FIELD_METRIC:{name}:{value}:{FAST|AVERAGE|SLOW}   (only if CrUX field data exists)
  LCP_ELEMENT:{nodeLabel}:{css selector}            (what the LCP element actually is — often text, not an image)
  LCP_PHASE:{phase label}:{ms}                      (time-to-first-byte / load delay / load time / render delay split —
                                                      a near-zero fetch phase with a large "Element render delay" means
                                                      the resource loaded fine and something on the main thread is
                                                      delaying paint; that's a scheduling problem, not a resource one —
                                                      see "sequence, don't cut" in references/b2-seo-guide.md)
  BLOCKING_RESOURCE:{url}:{wastedMs}                (render-blocking-insight items, sorted worst first)
  OPPORTUNITY:{audit_id}:{title}:{savings}
  DIAGNOSTIC:{audit_id}:{title}:{detail}
  ERROR:{reason}
  DONE:pagespeed:complete
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Google's official Core Web Vitals thresholds (lab-data audit ids -> (good_max, ni_max), lower is better).
THRESHOLDS = {
    "largest-contentful-paint": (2500, 4000),   # ms
    "first-contentful-paint":   (1800, 3000),   # ms
    "cumulative-layout-shift":  (0.1, 0.25),     # unitless
    "total-blocking-time":      (200, 600),      # ms
    "speed-index":              (3400, 5800),    # ms
    "interactive":              (3800, 7300),    # ms, Time to Interactive
}

METRIC_LABELS = {
    "largest-contentful-paint": "LCP",
    "first-contentful-paint":   "FCP",
    "cumulative-layout-shift":  "CLS",
    "total-blocking-time":      "TBT",
    "speed-index":              "SI",
    "interactive":              "TTI",
}

# CrUX field-data metric keys -> display label
FIELD_METRICS = {
    "LARGEST_CONTENTFUL_PAINT_MS": "LCP",
    "FIRST_CONTENTFUL_PAINT_MS":   "FCP",
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
    "INTERACTION_TO_NEXT_PAINT":   "INP",
    "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "TTFB",
}


def rate(audit_id, value):
    good_max, ni_max = THRESHOLDS[audit_id]
    if value <= good_max:
        return "GOOD"
    if value <= ni_max:
        return "NEEDS_IMPROVEMENT"
    return "POOR"


def fmt_value(audit_id, value):
    if audit_id == "cumulative-layout-shift":
        return f"{value:.2f}"
    return f"{value / 1000:.1f}s" if value >= 1000 else f"{round(value)}ms"


def read_dotenv_key(*names):
    """Parse .env in the project root for the first matching key, else None."""
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:]
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                if key.strip() in names:
                    val = val.strip().strip("\"'")
                    if val:
                        return val
    except FileNotFoundError:
        pass
    return None


def get_api_key():
    return (
        read_dotenv_key("GOOGLE_PAGESPEED_API_KEY", "PAGESPEED_API_KEY")
        or os.environ.get("GOOGLE_PAGESPEED_API_KEY")
        or os.environ.get("PAGESPEED_API_KEY")
    )


def fetch(url, strategy, categories, api_key):
    params = [("url", url), ("strategy", strategy)]
    for cat in categories:
        params.append(("category", cat))
    if api_key:
        params.append(("key", api_key))
    full_url = f"{API_ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "b2-seo-expert/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    parser.add_argument("--categories", default="performance,accessibility,best-practices,seo")
    args = parser.parse_args()

    if "localhost" in args.url or "127.0.0.1" in args.url:
        print("ERROR:local_url:PageSpeed cannot test localhost — publish first, then pass the live URL")
        sys.exit(1)

    categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    api_key = get_api_key()

    try:
        data = fetch(args.url, args.strategy, categories, api_key)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except json.JSONDecodeError:
            msg = body
        print(f"ERROR:api_error:{e.code}:{msg}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR:network:{e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR:unexpected:{e}")
        sys.exit(1)

    lighthouse = data.get("lighthouseResult")
    if not lighthouse:
        print("ERROR:no_lighthouse_result:API returned no lighthouseResult — check the URL is publicly reachable")
        sys.exit(1)

    print(f"STRATEGY:{args.strategy}")

    # ── Category scores ─────────────────────────────────────────
    for cat_id, cat in lighthouse.get("categories", {}).items():
        score = cat.get("score")
        if score is not None:
            print(f"SCORE:{cat_id}:{round(score * 100)}")

    audits = lighthouse.get("audits", {})

    # ── Core Web Vitals (lab data) ──────────────────────────────
    for audit_id, label in METRIC_LABELS.items():
        audit = audits.get(audit_id)
        if not audit or audit.get("numericValue") is None:
            continue
        value = audit["numericValue"]
        verdict = rate(audit_id, value)
        print(f"METRIC:{label}:{fmt_value(audit_id, value)}:{verdict}")

    # ── Core Web Vitals (field data / CrUX, if the site has enough real traffic) ──
    field_data = data.get("loadingExperience", {}).get("metrics", {})
    for key, label in FIELD_METRICS.items():
        metric = field_data.get(key)
        if not metric:
            continue
        percentile = metric.get("percentile")
        category = metric.get("category", "")  # FAST | AVERAGE | SLOW
        if key == "CUMULATIVE_LAYOUT_SHIFT_SCORE":
            value_str = f"{percentile / 100:.2f}"
        elif percentile is not None:
            value_str = f"{percentile / 1000:.1f}s" if percentile >= 1000 else f"{percentile}ms"
        else:
            value_str = "n/a"
        print(f"FIELD_METRIC:{label}:{value_str}:{category}")

    # ── LCP breakdown — what the LCP element actually is, and whether the
    # bottleneck is fetching it or rendering it (main-thread contention) ──
    lcp_breakdown = audits.get("lcp-breakdown-insight")
    if lcp_breakdown:
        for item in lcp_breakdown.get("details", {}).get("items", []):
            if item.get("type") == "table":
                for row in item.get("items", []):
                    dur = row.get("duration")
                    if dur is not None:
                        print(f"LCP_PHASE:{row.get('label', '')}:{round(dur)}ms")
            elif item.get("type") == "node":
                print(f"LCP_ELEMENT:{item.get('nodeLabel', '')}:{item.get('selector', '')}")

    # ── Render-blocking resources (specific URLs, not just the aggregate) ──
    render_blocking = audits.get("render-blocking-insight") or audits.get("render-blocking-resources")
    if render_blocking:
        items = render_blocking.get("details", {}).get("items", [])
        blockers = [(it.get("wastedMs", 0), it.get("url", "")) for it in items if it.get("url")]
        blockers.sort(reverse=True)
        for wasted_ms, url in blockers[:10]:
            print(f"BLOCKING_RESOURCE:{url}:{round(wasted_ms)}ms")

    # ── Opportunities (potential savings, sorted highest first) ─
    opportunities = []
    for audit_id, audit in audits.items():
        details = audit.get("details", {})
        if details.get("type") != "opportunity":
            continue
        savings_ms = details.get("overallSavingsMs", 0)
        savings_bytes = details.get("overallSavingsBytes", 0)
        if savings_ms <= 0 and savings_bytes <= 0:
            continue
        savings = f"{savings_ms}ms" if savings_ms > 0 else f"{round(savings_bytes / 1024)}KB"
        opportunities.append((savings_ms or savings_bytes, audit_id, audit.get("title", ""), savings))
    opportunities.sort(reverse=True)
    for _, audit_id, title, savings in opportunities[:10]:
        print(f"OPPORTUNITY:{audit_id}:{title}:{savings}")

    # ── Diagnostics — other failing audits not already covered above ──
    covered = set(METRIC_LABELS) | {a for _, a, _, _ in opportunities}
    diagnostics = []
    for audit_id, audit in audits.items():
        if audit_id in covered:
            continue
        score = audit.get("score")
        if score is None or score >= 0.9:
            continue
        if audit.get("scoreDisplayMode") not in ("binary", "numeric"):
            continue
        detail = audit.get("displayValue", "")
        diagnostics.append((score, audit_id, audit.get("title", ""), detail))
    diagnostics.sort()
    for _, audit_id, title, detail in diagnostics[:10]:
        print(f"DIAGNOSTIC:{audit_id}:{title}:{detail}")

    print("DONE:pagespeed:complete")


if __name__ == "__main__":
    main()
