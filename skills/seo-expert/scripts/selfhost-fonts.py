#!/usr/bin/env python3
"""
selfhost-fonts.py — Download Google Fonts as self-hosted woff2 (latin subset only).

Reads header.html, finds the Google Fonts CDN <link>, downloads the Latin-subset
woff2 files, generates @font-face CSS with font-display: swap, and prepends it to
styles.css (both theme and dist copies).

Usage:
  python3 selfhost-fonts.py audit                   # detect and report, no writes
  python3 selfhost-fonts.py fix THEME               # download + patch CSS

THEME defaults to value from website/b2.cfg if not passed.

Output format:
  DETECTED:google_fonts:{url}
  DETECTED:no_google_fonts
  FONT_FILE:{local_path}:{size_kb}KB
  FONT_FACE_BLOCK:{family}:{style}:{weight}
  PATCHED:styles:{path}
  PATCH_HEADER:remove:{line}
  PATCH_HEADER:add_preload:{link_tag}
  DONE:summary:{n_files} font files downloaded:{n_faces} @font-face blocks generated
"""

import re, sys, os, urllib.request

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


def find_google_fonts_url(header_path):
    with open(header_path) as f:
        content = f.read()
    m = re.search(r'<link[^>]+href="(https://fonts\.googleapis\.com/css2[^"]+)"', content)
    return m.group(1) if m else None


def fetch_css(url):
    req = urllib.request.Request(url, headers={"User-Agent": OG_UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def parse_latin_blocks(css):
    """Return list of dicts for each @font-face in the /* latin */ subset."""
    chunks = re.split(r'(/\*[^*]*\*/\s*)', css)
    blocks = []
    current_comment = ""
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk.startswith("/*"):
            current_comment = chunk
        elif chunk.startswith("@font-face") and current_comment == "/* latin */":
            family = re.search(r"font-family:\s*'([^']+)'", chunk)
            style  = re.search(r"font-style:\s*(\w+)", chunk)
            weight = re.search(r"font-weight:\s*([\d ]+)", chunk)
            url    = re.search(r"url\((https://[^)]+\.woff2)\)", chunk)
            urange = re.search(r"unicode-range:\s*([^\n;]+)", chunk)
            if family and url:
                blocks.append({
                    "family":  family.group(1),
                    "style":   style.group(1)  if style  else "normal",
                    "weight":  weight.group(1).strip() if weight else "400",
                    "url":     url.group(1),
                    "urange":  urange.group(1).strip() if urange else "",
                })
            current_comment = ""
    return blocks


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
    lines = ["/* Self-hosted fonts — latin subset only */"]
    for b in blocks:
        fname = url_to_local[b["url"]]
        lines.append(
            f"@font-face {{\n"
            f"  font-family: '{b['family']}';\n"
            f"  font-style: {b['style']};\n"
            f"  font-weight: {b['weight']};\n"
            f"  font-display: swap;\n"
            f"  src: url('/fonts/{fname}') format('woff2');\n"
            f"  unicode-range: {b['urange']};\n"
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


def preload_tags(url_to_local):
    """Return <link rel="preload"> tags for the most critical fonts."""
    critical = [
        fname for fname in url_to_local.values()
        if "playfair" in fname and "regular" in fname
    ] + [
        fname for fname in url_to_local.values()
        if "playfair" in fname and "italic" in fname
    ] + [
        fname for fname in url_to_local.values()
        if "source-serif" in fname and "regular" in fname
    ]
    seen = set()
    tags = []
    for fname in critical:
        if fname not in seen:
            seen.add(fname)
            tags.append(
                f'  <link rel="preload" href="/fonts/{fname}" '
                f'as="font" type="font/woff2" crossorigin />'
            )
    return tags


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

    fonts_url = find_google_fonts_url(header_path)
    if not fonts_url:
        print("DETECTED:no_google_fonts")
        return

    print(f"DETECTED:google_fonts:{fonts_url}")

    css = fetch_css(fonts_url)
    blocks = parse_latin_blocks(css)
    print(f"DETECTED:{len(blocks)} latin @font-face blocks from {len(set(b['url'] for b in blocks))} files")

    url_to_local = {}
    for b in blocks:
        if b["url"] not in url_to_local:
            url_to_local[b["url"]] = local_filename(b)

    font_css = build_font_face_css(blocks, url_to_local)
    preloads = preload_tags(url_to_local)

    # Lines to remove from header.html
    with open(header_path) as f:
        header_lines = f.readlines()

    remove_patterns = [
        r'fonts\.googleapis\.com',
        r'fonts\.gstatic\.com',
    ]
    lines_to_remove = [
        l.strip() for l in header_lines
        if any(re.search(p, l) for p in remove_patterns)
    ]

    if mode == "audit":
        print("\nWould download:")
        for url, fname in sorted(set(url_to_local.items())):
            print(f"  FONT_FILE:{FONTS_DIR}/{fname}")
        print("\nWould add to styles.css:")
        for b in blocks:
            print(f"  FONT_FACE_BLOCK:{b['family']}:{b['style']}:{b['weight']}")
        print("\nWould remove from header.html:")
        for l in lines_to_remove:
            print(f"  PATCH_HEADER:remove:{l}")
        print("\nWould add to header.html:")
        for tag in preloads:
            print(f"  PATCH_HEADER:add_preload:{tag.strip()}")
        print(f"\nDONE:audit:{len(url_to_local)} font files:{len(blocks)} @font-face blocks")
        return

    # Fix mode — download and patch
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

    # Patch styles.css in both theme and dist
    for css_path in [
        f"website/theme/{theme}/styles.css",
        "website/dist/styles.css",
    ]:
        if os.path.exists(css_path):
            if prepend_to_css(css_path, font_css):
                print(f"PATCHED:styles:{css_path}")
            else:
                print(f"SKIP:styles_already_patched:{css_path}")

    # Report header.html changes (caller must apply these)
    print("\n--- Header.html changes required ---")
    print("REMOVE these lines from header.html:")
    for l in lines_to_remove:
        print(f"  {l}")
    print("\nADD these preload tags (before <link rel='stylesheet'>):")
    for tag in preloads:
        print(f"  {tag.strip()}")

    n_faces = len(blocks)
    print(f"\nDONE:summary:{downloaded} font files downloaded:{n_faces} @font-face blocks generated")
    print("NOTE: Update header.html manually using the REMOVE/ADD instructions above.")
    print("NOTE: Rebuild with assemble.sh after updating header.html.")


if __name__ == "__main__":
    main()
