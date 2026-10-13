#!/usr/bin/env python3
"""
b2 - check whether GEMINI_API_KEY is available
Checks: .env file → GEMINI_API_KEY environment variable
Exit code: 0 if found, 1 if missing
Stdout: OK:<source> or MISSING
"""
import os, sys

def read_dotenv(path):
    """Parse a .env file and return the value of GEMINI_API_KEY, or None."""
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
                    if key.strip() == 'GEMINI_API_KEY':
                        return val.strip().strip('"\'') or None
    except FileNotFoundError:
        pass
    return None

def check():
    val = read_dotenv('.env')
    if val:
        print('OK:.env')
        return True
    if os.environ.get('GEMINI_API_KEY', '').strip():
        print('OK:env')
        return True
    print('MISSING')
    return False

sys.exit(0 if check() else 1)
