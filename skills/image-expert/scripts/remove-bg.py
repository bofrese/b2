#!/usr/bin/env python3
"""
b2 - remove image background using rembg
Usage: python3 remove-bg.py <input_path> [output_path]
Output: transparent PNG. Defaults to <input_stem>-nobg.png alongside the input file.
Exit codes: 0 success, 1 rembg not installed, 2 error
"""
import sys, os
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: remove-bg.py <input_path> [output_path]", file=sys.stderr)
        sys.exit(2)

    input_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.parent / f"{input_path.stem}-nobg.png"

    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        print("NOT_INSTALLED", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, "rb") as f:
            result = remove(f.read())
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(result)
        print(f"SAVED:{output_path}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
