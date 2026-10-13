#!/usr/bin/env python3
"""
b2 image generation - Gemini API
Usage: python3 generate.py <aspect_ratio> <output_path> [model]
Prompt: read from stdin
API key: .env file → GEMINI_API_KEY env var

Aspect ratios: 1:1  3:2  2:3  4:3  3:4  16:9  9:16  4:5  5:4  21:9
Exit codes: 0 success, 1 error
Stdout: SAVED:<path> on success, MODEL_TEXT:<text> if model returns text
"""
import json, sys, base64, urllib.request, urllib.error, os

def resolve_api_key():
    """Check .env file first, then GEMINI_API_KEY environment variable."""
    try:
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('export '):
                    line = line[7:]
                if '=' in line:
                    key, _, val = line.partition('=')
                    if key.strip() == 'GEMINI_API_KEY':
                        val = val.strip().strip('"\'')
                        if val:
                            return val
    except FileNotFoundError:
        pass
    return os.environ.get('GEMINI_API_KEY', '').strip()

def main():
    if len(sys.argv) < 3:
        print("Usage: generate.py <aspect_ratio> <output_path> [model]", file=sys.stderr)
        sys.exit(1)

    aspect_ratio = sys.argv[1]
    output_path  = sys.argv[2]
    model        = sys.argv[3] if len(sys.argv) > 3 else "gemini-2.0-flash-preview-image-generation"
    prompt       = sys.stdin.read().strip()

    if not prompt:
        print("ERROR: prompt is empty (pass via stdin)", file=sys.stderr)
        sys.exit(1)

    api_key = resolve_api_key()
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env or environment", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio}
        }
    }).encode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(url, data=payload, headers={
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    })

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    saved = False
    for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inline_data" in part:
            out_dir = os.path.dirname(output_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(part["inline_data"]["data"]))
            print(f"SAVED:{output_path}")
            saved = True
        elif "text" in part and part["text"].strip():
            print(f"MODEL_TEXT:{part['text']}")

    if not saved:
        print("ERROR: no image in response", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
