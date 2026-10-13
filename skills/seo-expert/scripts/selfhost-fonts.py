#!/usr/bin/env python3
"""
selfhost-fonts.py - Download CDN-hosted webfonts as self-hosted woff2 (latin
subset only where the provider splits by subset).

Detects ANY external font-CDN stylesheet in header.html, not just Google
Fonts - a design can easily load two or three foundries at once (e.g. Google
Fonts for body text, Fontshare/Adobe Fonts/Bunny Fonts for display headings),
and a fix that only handles one leaves the others as an invisible render-
blocking cost that "looks handled" because a similar-looking fix already ran.
Detection works by fetching each external <link rel="stylesheet"> and checking
whether the response contains @font-face - provider-agnostic, no per-CDN
special-casing needed.

Note on variable fonts: modern Google Fonts responses often serve ONE woff2
file covering an entire weight range, with several @font-face blocks (one per
discrete weight) all pointing at that same file. This is standard, correct
variable-font technique - browsers instantiate the right weight from the
file's axis - not a bug. Don't "fix" it into separate per-weight downloads.

Reads header.html, downloads the font files, generates @font-face CSS with
font-display: swap, prepends it to styles.css (theme + dist copies), and
patches header.html directly: removes the CDN <link>/<preconnect> tags, adds
preload tags for the base (400, non-italic) weight of each family.

Usage:
  python3 selfhost-fonts.py audit                   # detect and report, no writes
  python3 selfhost-fonts.py fix THEME               # download + patch CSS + patch header.html

THEME defaults to value from website/b2.cfg if not passed.

Output format:
  DETECTED:font_cdn:{url}
  DETECTED:no_font_cdn
  FONT_FILE:{local_path}:{size_kb}KB
  FONT_FACE_BLOCK:{family}:{style}:{weight}
  PATCHED:styles:{path}
  PATCHED:header:{path}
  DONE:summary:{n_files} font files downloaded:{n_faces} @font-face blocks generated
"""

import re, sys, os, urllib.request
from urllib.parse import urlparse

OG_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
         "AppleWebKit/537.36 (KHTML, like Gecko) "
         "Chrome/120.0.0.0 Safari/537.36")

FONTS_DIR = "website/dist/fonts"


def get_theme(argv):
    cfg_path = "website/b2.cfg"
    theme = "b2"
    if os.path.exists(cfg_path):
        for line in open(cfg_path):
            if line.startswith("THEME="):
                theme = line.strip().split("=", 1)[1]
                break
    for arg in argv:
        if not arg.startswith("-") and arg not in ("audit", "fix"):
            theme = arg
    return theme


def find_stylesheet_links(header_path):
    """Return every external (https://) <link rel="stylesheet" href="..."> in
    header.html, regardless of attribute order. Provider-agnostic - callers
    fetch each and check for @font-face to decide which are font CDNs."""
    with open(header_path) as f:
        content = f.read()
    hrefs = set()
    for tag in re.findall(r"<link\s[^>]*>", content):
        if "stylesheet" not in tag:
            continue
        m = re.search(r'href="(https?://[^"]+)"', tag)
        if m:
            hrefs.add(m.group(1))
    return sorted(hrefs)


def fetch_css(url):
    req = urllib.request.Request(url, headers={"User-Agent": OG_UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def parse_font_face_blocks(css):
    """Return @font-face blocks. If the CSS is split into subset comments
    (Google Fonts convention: /* latin */, /* cyrillic */, ...), keep only
    the latin subset. If a provider ships no subset comments at all (many
    non-Google foundries - one universal file per weight), keep everything."""
    chunks = re.split(r'(/\*[^*]*\*/\s*)', css)
    all_blocks = []
    latin_blocks = []
    has_subset_comments = False
    current_comment = ""
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk.startswith("/*"):
            current_comment = chunk.strip("/* \t\n").strip()
            has_subset_comments = True
        elif chunk.startswith("@font-face"):
            family = re.search(r"font-family:\s*['\"]([^'\"]+)['\"]", chunk)
            style  = re.search(r"font-style:\s*(\w+)", chunk)
            weight = re.search(r"font-weight:\s*([\d ]+)", chunk)
            url    = re.search(r"url\(\s*['\"]?([^'\")]+\.woff2)['\"]?\s*\)", chunk)
            urange = re.search(r"unicode-range:\s*([^\n;]+)", chunk)
            if family and url:
                raw_url = url.group(1)
                if raw_url.startswith("//"):
                    raw_url = "https:" + raw_url
                block = {
                    "family":  family.group(1),
                    "style":   style.group(1)  if style  else "normal",
                    "weight":  weight.group(1).strip() if weight else "400",
                    "url":     raw_url,
                    "urange":  urange.group(1).strip() if urange else "",
                }
                all_blocks.append(block)
                if current_comment.lower() == "latin":
                    latin_blocks.append(block)
            current_comment = ""
    return latin_blocks if (has_subset_comments and latin_blocks) else all_blocks


def local_filename(block):
    fam = block["family"].lower().replace(" ", "-")
    sty = "italic" if block["style"] == "italic" else "regular"
    wgt = block["weight"].replace(" ", "-")
    return f"{fam}-{wgt}-{sty}.woff2"


def download_file(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": OG_UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def build_font_face_css(blocks, url_to_local):
    lines = ["/* Self-hosted fonts - latin subset only */"]
    for b in blocks:
        fname = url_to_local[b["url"]]
        unicode_line = f"\n  unicode-range: {b['urange']};" if b["urange"] else ""
        lines.append(
            f"@font-face {{\n"
            f"  font-family: '{b['family']}';\n"
            f"  font-style: {b['style']};\n"
            f"  font-weight: {b['weight']};\n"
            f"  font-display: swap;\n"
            f"  src: url('/fonts/{fname}') format('woff2');{unicode_line}\n"
            f"}}"
        )
    return "\n".join(lines) + "\n"


def prepend_to_css(css_path, font_css):
    with open(css_path) as f:
        existing = f.read()
    if "Self-hosted fonts" in existing:
        return False
    with open(css_path, "w") as f:
        f.write(font_css + "\n" + existing)
    return True


def preload_tags(blocks, url_to_local):
    """Preload the base (400, non-italic) weight of each distinct family - 
    that's the one most likely to gate first paint of visible text."""
    seen_families = set()
    tags = []
    for b in blocks:
        if b["style"] == "italic" or b["family"] in seen_families:
            continue
        if b["weight"] not in ("400", "normal", ""):
            continue
        seen_families.add(b["family"])
        fname = url_to_local[b["url"]]
        tags.append(
            f'  <link rel="preload" href="/fonts/{fname}" '
            f'as="font" type="font/woff2" crossorigin />'
        )
    return tags


def patch_header(header_path, lines_to_remove, preload_tags_list):
    with open(header_path) as f:
        lines = f.readlines()

    remove_set = set(lines_to_remove)
    kept = [l for l in lines if l.strip() not in remove_set]

    if preload_tags_list:
        already_present = any(
            any(tag.strip() in l for tag in preload_tags_list) for l in kept
        )
        if not already_present:
            marker = '<link rel="stylesheet" href="/styles.css" />'
            new_kept = []
            inserted = False
            for l in kept:
                if not inserted and marker in l:
                    indent = l[: len(l) - len(l.lstrip())]
                    for tag in preload_tags_list:
                        new_kept.append(indent + tag.strip() + "\n")
                    inserted = True
                new_kept.append(l)
            kept = new_kept

    with open(header_path, "w") as f:
        f.writelines(kept)


def main():
    mode = "audit"
    for arg in sys.argv[1:]:
        if arg == "fix":
            mode = "fix"
        elif arg == "audit":
            mode = "audit"

    theme = get_theme(sys.argv[1:])
    header_path = f"website/theme/{theme}/header.html"

    if not os.path.exists(header_path):
        print(f"ERROR: header not found: {header_path}")
        sys.exit(1)

    candidate_links = find_stylesheet_links(header_path)
    font_cdns = []
    for link_url in candidate_links:
        try:
            css_text = fetch_css(link_url)
        except Exception:
            continue
        if "@font-face" in css_text:
            font_cdns.append((link_url, css_text))

    if not font_cdns:
        print("DETECTED:no_font_cdn")
        return

    all_blocks = []
    for fonts_url, css in font_cdns:
        print(f"DETECTED:font_cdn:{fonts_url}")
        blocks = parse_font_face_blocks(css)
        print(f"DETECTED:{len(blocks)} @font-face blocks from {len(set(b['url'] for b in blocks))} files")
        all_blocks.extend(blocks)

    url_to_local = {}
    for b in all_blocks:
        if b["url"] not in url_to_local:
            url_to_local[b["url"]] = local_filename(b)

    font_css = build_font_face_css(all_blocks, url_to_local)
    preloads = preload_tags(all_blocks, url_to_local)

    # Lines to remove from header.html: the CDN stylesheet <link> itself, any
    # <link rel="preconnect"> pointing at that CDN's domain, and the same for
    # any domain the actual font FILES are served from (fonts.gstatic.com is a
    # different domain from fonts.googleapis.com, for example).
    with open(header_path) as f:
        header_lines = f.readlines()

    font_domains = {urlparse(u).netloc for u, _ in font_cdns}
    font_domains |= {urlparse(b["url"]).netloc for b in all_blocks}
    cdn_hrefs = {u for u, _ in font_cdns}

    def line_matches(line):
        if any(href in line for href in cdn_hrefs):
            return True
        if "preconnect" in line and any(dom in line for dom in font_domains):
            return True
        return False

    lines_to_remove = [l.strip() for l in header_lines if line_matches(l)]

    if mode == "audit":
        print("\nWould download:")
        for url, fname in sorted(set(url_to_local.items())):
            print(f"  FONT_FILE:{FONTS_DIR}/{fname}")
        print("\nWould add to styles.css:")
        for b in all_blocks:
            print(f"  FONT_FACE_BLOCK:{b['family']}:{b['style']}:{b['weight']}")
        print("\nWould remove from header.html:")
        for l in lines_to_remove:
            print(f"  PATCH_HEADER:remove:{l}")
        print("\nWould add to header.html:")
        for tag in preloads:
            print(f"  PATCH_HEADER:add_preload:{tag.strip()}")
        print(f"\nDONE:audit:{len(url_to_local)} font files:{len(all_blocks)} @font-face blocks")
        return

    # Fix mode - download, patch styles.css, patch header.html directly
    os.makedirs(FONTS_DIR, exist_ok=True)
    downloaded = 0
    for url, fname in url_to_local.items():
        dest = os.path.join(FONTS_DIR, fname)
        if not os.path.exists(dest):
            size = download_file(url, dest)
            kb = size // 1024
            print(f"FONT_FILE:{dest}:{kb}KB")
            downloaded += 1
        else:
            kb = os.path.getsize(dest) // 1024
            print(f"FONT_FILE:{dest}:{kb}KB (already exists)")

    for css_path in [
        f"website/theme/{theme}/styles.css",
        "website/dist/styles.css",
    ]:
        if os.path.exists(css_path):
            if prepend_to_css(css_path, font_css):
                print(f"PATCHED:styles:{css_path}")
            else:
                print(f"SKIP:styles_already_patched:{css_path}")

    patch_header(header_path, lines_to_remove, preloads)
    print(f"PATCHED:header:{header_path}")

    n_faces = len(all_blocks)
    print(f"\nDONE:summary:{downloaded} font files downloaded:{n_faces} @font-face blocks generated")
    print("NOTE: Rebuild (make / assemble.sh) to pick up the patched header.html and styles.css.")


if __name__ == "__main__":
    main()
