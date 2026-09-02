# Mnemo

Self-hosted, project-scoped memory for Claude Code and Codex. No cloud
services, no paid APIs — everything runs on your own machine.

Mnemo gives an AI coding agent a place to remember things across
sessions: architecture decisions, in-progress debugging state, a
running project brief — scoped so a session in one repo can never see
another repo's memory by accident.

## What it does

- **`memory_add` / `memory_search`** — write and recall memories, hard-scoped to the current project.
- **Checkpoint/resume** — say "checkpoint this" before a long session ends; it's recalled automatically the next time you start one.
- **Named documents** — a project overview or running dev log that updates in place instead of piling up, also auto-loaded every session.
- **`memory_search_global`** — the one explicit, deliberate escape hatch for a genuinely cross-project question.
- **`mnemo import`** — bulk-load an existing file into a project's memory.
- **`mnemo graph`** — a real, embedding-similarity graph of your memories, rendered locally and opened in your browser.

## Requirements

- macOS or Linux
- [Docker](https://www.docker.com/) or [OrbStack](https://orbstack.dev/) (Qdrant runs in a container)
- [Ollama](https://ollama.com/), with `nomic-embed-text` pulled
- [uv](https://docs.astral.sh/uv/)

## Quick start (Claude Code plugin)

Prerequisites: [Docker](https://www.docker.com/)/[OrbStack](https://orbstack.dev/)
and [Ollama](https://ollama.com/) installed (running is enough — `/mnemo-setup`
starts Qdrant and checks for the embedding model for you).

Inside Claude Code, in whichever repo you want memory in:

```
/plugin marketplace add pacheco20222/mnemo
/plugin install mnemo
/mnemo-setup my-first-project
```

That starts Qdrant if it isn't already running, checks for the
`nomic-embed-text` model, and writes `.mcp.json` (and, if you want it,
the checkpoint/resume hook) for this repo. Restart the session and
`memory_add`/`memory_search` are available. Run `/mnemo-setup` again
with a different project name in any other repo — no cloning, no
hand-edited config.

## Quick start (manual / Codex)

```bash
git clone git@github.com:pacheco20222/mnemo.git
cd mnemo
docker compose up -d
ollama pull nomic-embed-text
uv run mnemo setup --project my-first-project
```

Paste the printed config into your repo's `.mcp.json`, or run the printed
`codex mcp add` command for Codex. See [docs/INSTALL.md](docs/INSTALL.md)
for the full walkthrough, including the real difference between how
Claude Code and Codex scope projects.

## How it works

Qdrant (vector store) + Ollama (`nomic-embed-text`, local embeddings) +
FastMCP (the MCP server itself, stdio transport). See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design and
every tool's exact signature.

## License

MIT — see [LICENSE](LICENSE).
