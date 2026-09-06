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
- [uv](https://docs.astral.sh/uv/)

No GPU, no separate embedding service — `fastembed` runs locally on CPU
and installs like any other Python dependency.

## Quick start (Claude Code plugin)

Prerequisite: [Docker](https://www.docker.com/)/[OrbStack](https://orbstack.dev/)
installed (running is enough — `/mnemo:mnemo-register` starts Qdrant for you).

Inside Claude Code, in whichever repo you want memory in:

```
/plugin marketplace add pacheco20222/mnemo
/plugin install mnemo
/mnemo:mnemo-register my-first-project
```

That's it — nothing gets written into this repo. `/mnemo:mnemo-register`
starts Qdrant if it isn't already running, then registers this folder
under that project name in a small file outside any repo
(`~/.mnemo/projects.json`). The first `memory_add` you make downloads
the embedding model automatically (~500MB, one-time). `memory_add`/
`memory_search` work immediately, same session, no restart. Run
`/mnemo:mnemo-register` again with a different project name in any other
repo — same plugin install, no per-repo config at all.

## Quick start (manual / Codex)

```bash
git clone git@github.com:pacheco20222/mnemo.git
cd mnemo
docker compose up -d
uv run mnemo setup --project my-first-project
```

For Claude Code: paste the printed `.mcp.json` block into your repo. For
Codex, run the command it prints — it looks like this, with your real
path and project name filled in:

```bash
codex mcp add mnemo --env MNEMO_PROJECT=my-first-project -- uv run --directory /absolute/path/to/mnemo mnemo
```

Run that from anywhere — `--directory` points at this mnemo clone, not
the project you're tracking; `MNEMO_PROJECT` is what fixes the project,
not your current directory. See [docs/INSTALL.md](docs/INSTALL.md) for
the full walkthrough, including the real difference between how Claude
Code and Codex scope projects.

## How it works

Qdrant (vector store) + fastembed (`nomic-embed-text-v1.5`, local
CPU embeddings, no separate service) + FastMCP (the MCP server itself,
stdio transport). See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design and
every tool's exact signature.

## Upgrading from 1.x

2.0.0 changes the embedding backend (Ollama → fastembed) — see
[CHANGELOG.md](CHANGELOG.md). Old and new embeddings share the same 768
dimensions but are **not** the same vector space, and Qdrant can't detect
the difference. If you're upgrading an existing install, either start a
fresh `memories` collection, or expect old memories to rank essentially
randomly against new ones in semantic search until you re-add them.

## License

MIT — see [LICENSE](LICENSE).
