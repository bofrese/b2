#!/usr/bin/env python3
"""
minify-css.py — Safe, dependency-free CSS minifier for b2's build step.

Strips comments, collapses whitespace, trims redundant whitespace around
punctuation. No third-party dependencies (pure stdlib) — b2 must not assume
Node/npm are available in the user's environment. CSS has no regex-literal or
template-literal ambiguity, so full comment/whitespace stripping is safe here
(unlike JS — see minify-js.py for why that one is deliberately conservative).

Usage:
  python3 minify-css.py <input.css> <output.css>
  python3 minify-css.py <input.css>              # print to stdout

Idempotent: minifying already-minified CSS is a safe no-op.
"""
import re
import sys


def minify_css(css):
    # Strip /* ... */ comments (including those spanning multiple lines).
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    # Collapse all whitespace runs (including newlines) to a single space.
    css = re.sub(r'\s+', ' ', css)
    # Trim whitespace around punctuation that never needs it.
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    # Drop the trailing semicolon before a closing brace — redundant.
    css = re.sub(r';}', '}', css)
    return css.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: minify-css.py <input.css> [output.css]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        original = f.read()

    minified = minify_css(original)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(minified)
        before, after = len(original.encode("utf-8")), len(minified.encode("utf-8"))
        print(f"MINIFIED:{sys.argv[1]}:{before}B -> {after}B (-{before - after}B)")
    else:
        sys.stdout.write(minified)


if __name__ == "__main__":
    main()
