#!/usr/bin/env python3
"""
minify-js.py — Conservative, dependency-free JS minifier for b2's build step.

Deliberately NOT a full minifier. Full-scale JS minification requires a real
parser to disambiguate `/` (division vs regex literal), template literals,
and string escaping — getting that wrong silently corrupts production code.
b2 must not assume Node/npm are available to reach for a real one (esbuild,
terser, etc.), so this only does what's safe to do with confidence:

  - Remove comments that occupy their OWN line (line/block comments where the
    entire line, once trimmed, is comment — never comments that share a line
    with real code, since detecting `//` mid-line risks misreading a regex
    literal or a division operator as a comment start).
  - Strip leading indentation and trailing whitespace per line (irrelevant to
    JS parsing — only newlines matter for ASI, and every original line break
    is preserved exactly, never merged).
  - Collapse runs of blank lines to one.

Skips comment-stripping entirely while inside a multi-line template literal
(tracked via unescaped backtick parity), so a `// looks like a comment` inside
a template string is never touched.

Usage:
  python3 minify-js.py <input.js> <output.js>
  python3 minify-js.py <input.js>              # print to stdout

Idempotent: minifying already-minified JS is a safe no-op.
"""
import re
import sys


def _unescaped_backtick_count(line):
    count = 0
    i = 0
    while i < len(line):
        if line[i] == '\\':
            i += 2
            continue
        if line[i] == '`':
            count += 1
        i += 1
    return count


def minify_js(js):
    lines = js.split('\n')
    out = []
    in_block_comment = False
    in_template = False

    for line in lines:
        if in_template:
            out.append(line)
            if _unescaped_backtick_count(line) % 2 == 1:
                in_template = False
            continue

        if in_block_comment:
            if '*/' in line:
                idx = line.index('*/') + 2
                rest = line[idx:]
                in_block_comment = False
                if rest.strip():
                    out.append(rest.strip())
            continue

        stripped = line.strip()

        if stripped.startswith('//'):
            continue

        if stripped.startswith('/*'):
            if '*/' in line:
                idx = line.index('*/') + 2
                rest = line[idx:]
                if rest.strip():
                    out.append(rest.strip())
            else:
                in_block_comment = True
            continue

        out.append(stripped)
        if _unescaped_backtick_count(line) % 2 == 1:
            in_template = True

    # Collapse runs of blank lines to a single blank line.
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(out))
    return result.strip() + '\n'


def main():
    if len(sys.argv) < 2:
        print("Usage: minify-js.py <input.js> [output.js]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        original = f.read()

    minified = minify_js(original)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(minified)
        before, after = len(original.encode("utf-8")), len(minified.encode("utf-8"))
        print(f"MINIFIED:{sys.argv[1]}:{before}B -> {after}B (-{before - after}B)")
    else:
        sys.stdout.write(minified)


if __name__ == "__main__":
    main()
