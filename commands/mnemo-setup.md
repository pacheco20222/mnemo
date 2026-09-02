---
description: Wire this repo up to use the mnemo memory server (starts Qdrant if needed, writes .mcp.json and, optionally, the SessionStart hook)
argument-hint: [project-name]
allowed-tools: Bash, Read, Write, Edit
---

Set up this repo to use mnemo, scoped to project "$1".

If `$1` is empty, ask the user for the project name before doing anything else — don't fall back to a placeholder.

1. Check whether Qdrant is already reachable (`curl -s http://localhost:6333/collections`). If not, run `docker compose -f ${CLAUDE_PLUGIN_ROOT}/docker-compose.yml up -d` to start it (this is the plugin's own bundled compose file — safe and idempotent to run even if some other Qdrant is already up on port 6333, in which case compose will just report the container already exists or fail cleanly if the port's taken by something unrelated; explain either outcome to the user rather than guessing).
2. Check whether Ollama has the embedding model (`ollama list` should include `nomic-embed-text`). If it's missing, tell the user to run `ollama pull nomic-embed-text` themselves — don't pull it for them, it's a real multi-hundred-MB download.
3. Run `uv run --directory ${CLAUDE_PLUGIN_ROOT} mnemo setup --project $1` and read its output. It prints three things: a `.mcp.json` block, an optional `.claude/settings.json` SessionStart hook block, and a `codex mcp add` command.
4. Write or merge the `.mcp.json` block into this repo's `.mcp.json` at the repo root. If `.mcp.json` already exists, merge the `"mnemo"` key into its existing `"mcpServers"` object rather than overwriting the file — preserve every other server already configured there.
5. Ask the user whether they also want the SessionStart hook (auto-loads the latest checkpoint and project overview document at the start of every session). If yes, write or merge the hook block into this repo's `.claude/settings.json` the same way — merge the `"SessionStart"` entry into the existing `"hooks"` object if the file already exists, don't overwrite unrelated settings.
6. Print the `codex mcp add` command for the user to run themselves in their own terminal if they use Codex too — do not run it for them.
7. Confirm exactly what was written (which files, which keys) and tell the user to restart Claude Code (or start a new session) for the MCP server and hook to take effect.
