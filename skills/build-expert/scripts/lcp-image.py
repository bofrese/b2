import re, sys
with open(sys.argv[1]) as f:
    content = f.read()
for line in content.splitlines():
    if 'fetchpriority' in line and 'high' in line and '<img' in line:
        m = re.search(r'src=["\']([^"\']+)["\']', line)
        if m:
            print(m.group(1))
            break
