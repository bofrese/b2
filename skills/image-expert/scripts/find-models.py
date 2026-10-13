#!/usr/bin/env python3
"""
b2 - list available Gemini image-capable models
Usage: python3 find-models.py
API key: .env file → GEMINI_API_KEY env var
Output: one model ID per line (without the 'models/' prefix), ready to pass to generate.py
"""
import urllib.request, json, os, sys

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

key = resolve_api_key()
if not key:
    print("ERROR: GEMINI_API_KEY not found in .env or environment", file=sys.stderr)
    sys.exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
with urllib.request.urlopen(url) as r:
    data = json.loads(r.read())

for m in data.get("models", []):
    name = m.get("name", "")
    if "image" in name.lower() or "imagen" in name.lower():
        # Strip 'models/' prefix - generate.py constructs its own URL
        print(name.removeprefix("models/"))
