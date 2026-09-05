---
description: Register this repo with mnemo (starts Qdrant if needed, no files written into this repo)
argument-hint: [project-name]
allowed-tools: Bash, Read
---

Register this repo with mnemo, as project "$1".

If `$1` is empty, ask the user for the project name before doing anything else — don't guess one.

1. Check whether Qdrant is already reachable (`curl -s http://localhost:6333/collections`). If not, run `docker compose -f ${CLAUDE_PLUGIN_ROOT}/docker-compose.yml up -d` to start it (the plugin's own bundled compose file — safe and idempotent even if some other Qdrant is already up on port 6333, in which case explain the outcome to the user rather than guessing).
2. Run `uv run --project ${CLAUDE_PLUGIN_ROOT} mnemo register --project $1` from the current directory. This writes nothing into this repo — it records this folder's absolute path against the project name in a registry outside any repo (`~/.mnemo/projects.json`).
3. Tell the user `memory_add`/`memory_search`/etc. work immediately, in this same session — no restart needed, since the project resolves fresh on every call. The first `memory_add` downloads the embedding model automatically (~500MB, one-time) — mention this so it isn't a silent surprise. The checkpoint/project-overview auto-load hook takes effect starting the *next* session (inherent to what a `SessionStart` hook is). That's it — don't mention Codex, or any other tool, unless the user asks.
