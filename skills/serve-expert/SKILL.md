---
name: serve-expert
description: This skill should be used when the user runs "/b2:serve", asks to "start a local server", "preview the site", "serve the site locally", or "run the dev server". Starts a local HTTP server on website/dist/ and reports the URL.
---

# b2 Serve Expert

Start a local web server on `website/dist/` and report the URL. Does not watch for changes.

---

## Prerequisite Check

Check whether `website/dist/` exists and contains HTML files (Bash tool):

```bash
root="$(pwd)"
ls "$root/website/dist"/*.html 2>/dev/null | head -1
```

If no HTML files found, stop:

> "No built pages found. Run `/b2:build` first to assemble dist/."

---

## Check for an Already-Running Server

A server may already be bound to port 8099 from a previous session — possibly serving the wrong directory (e.g. `website/` instead of `website/dist/`, left over from a manual start or an interrupted process). A 200 response alone does not confirm it's serving the right content.

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8099/ 2>/dev/null || echo "unreachable"
```

If it responds, verify it's actually serving `dist/` — pick one filename from `website/dist/*.html` other than `index.html` (if any exist) and request it:

```bash
curl -s -o /dev/null -w "%{http_code}" "http://localhost:8099/{that-filename}"
```

- **200:** the running server is correct — report the existing URL and stop, don't start a second one.
- **404 (or the port is occupied by something that doesn't serve this site):** the server is stale or misconfigured. Do not kill it silently — report what's bound to the port if discoverable (`lsof -i :8099` on macOS/Linux, best-effort — skip quietly if unavailable, e.g. on Windows) and ask the user: kill and restart on 8099, or use a different port?

---

## Detect Available Server

Try servers in this priority order (Bash tool):


1. **Python 3** — portable, usually available:
   ```bash
   python3 --version 2>/dev/null && echo "python3"
   ```

2. **npx serve** — Node.js based:
   ```bash
   npx --yes serve --version 2>/dev/null && echo "npx-serve"
   ```

3. **Docker Compose** — if `website/docker-compose.yml` exists and `docker compose` is available:
   ```bash
   [ -f "$(pwd)/website/docker-compose.yml" ] && docker compose version 2>/dev/null && echo "docker"
   ```

Use the first one that succeeds.

---

## Start the Server

**Python 3:**
```bash
cd "$(pwd)/website/dist" && python3 -m http.server 8099
```
Report: `"Server running at http://localhost:8099"`

**npx serve:**
```bash
cd "$(pwd)/website/dist" && npx serve -p 8099
```
Report: `"Server running at http://localhost:8099"`

**Docker Compose:** Read `website/docker-compose.yml` to find the port mapping. Start:
```bash
cd website && docker compose up
```
Report: `"Server running at http://localhost:{port}"`


**None available:** Stop with:

> "No local server found. Install one of:
> - Python 3: already installed on most systems (`python3 -m http.server 8099`)
> - Node.js: `npx serve` (run from website/dist/)
> - Docker: start Docker Desktop, then run `/b2:serve` again"
