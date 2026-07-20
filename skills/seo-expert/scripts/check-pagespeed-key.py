#!/usr/bin/env python3
"""
b2 — check whether a PageSpeed Insights API key is available
Checks: .env file → GOOGLE_PAGESPEED_API_KEY/PAGESPEED_API_KEY environment variable
Exit code: 0 if found, 1 if missing
Stdout: OK:<source> or MISSING
"""
import os, sys

NAMES = ("GOOGLE_PAGESPEED_API_KEY", "PAGESPEED_API_KEY")

def read_dotenv(path):
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('export '):
                    line = line[7:]
                if '=' in line:
                    key, _, val = line.partition('=')
                    if key.strip() in NAMES:
                        val = val.strip().strip('"\'')
                        if val:
                            return val
    except FileNotFoundError:
        pass
    return None

def check():
    val = read_dotenv('.env')
    if val:
        print('OK:.env')
        return True
    for name in NAMES:
        if os.environ.get(name, '').strip():
            print('OK:env')
            return True
    print('MISSING')
    return False

sys.exit(0 if check() else 1)
