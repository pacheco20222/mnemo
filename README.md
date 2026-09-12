# Mnemo

Self-hosted, project-scoped memory for Claude Code, Cursor, and Codex.
No cloud services, no paid APIs — everything runs on your own machine.

Mnemo gives an AI coding agent a place to remember things across
sessions: architecture decisions, in-progress debugging state, a
running project brief — scoped so a session in one repo can never see
another repo's memory by accident.

## What it does

- **`memory_add` / `memory_search`** — write and recall memories, hard-scoped to the current project.
- **Checkpoint/resume** — say "checkpoint this" before a long session ends; it's recalled automatically the next time you start one.
- **Named documents** — a project overview or running dev log that updates in place instead of piling up, also auto-loaded every session.
- **`memory_search_global`** — the one explicit, deliberate escape hatch for a genuinely cross-project question.
- **`mnemo import`** — bulk-load an existing file into a project's memory. Run yourself, from a terminal — see [docs/INSTALL.md §6](docs/INSTALL.md#6-running-mnemos-other-commands-import-graph).
- **`mnemo graph`** — a real, embedding-similarity graph of your memories, rendered locally and opened in your browser. Same terminal invocation as `import` above.

## Requirements

- macOS, Linux, or Windows (PowerShell 5.1+/pwsh, or WSL2 — anything
  Linux-based in this repo just works unmodified under WSL2)
- [Docker](https://www.docker.com/) or [OrbStack](https://orbstack.dev/) (Qdrant runs in a container)
- [uv](https://docs.astral.sh/uv/)

No GPU, no separate embedding service — `fastembed` runs locally on CPU
and installs like any other Python dependency. Mnemo initializes it only
when the first memory tool is called, so loading or downloading the model
does not delay the MCP startup handshake on Windows, macOS, or Linux.

## Quick start (Claude Code plugin)

Prerequisite: [Docker](https://www.docker.com/)/[OrbStack](https://orbstack.dev/)
installed (running is enough — `/mnemo:mnemo-register` starts Qdrant for you).

Inside Claude Code, in whichever repo you want memory in:

```
/plugin marketplace add pacheco20222/mnemo
/plugin install mnemo --scope project
/mnemo:mnemo-register my-first-project
```

`--scope project` keeps Mnemo scoped to this one repo — installing it
here doesn't make it show up in any other project you open. That's the
recommended default: each repo gets its own isolated memory, and
nothing connects to anything else unless you say so. Want it available
in another repo too? Run the same three commands there (with that
repo's own project name) — nothing gets written into either repo
either way. `/mnemo:mnemo-register` starts Qdrant if it isn't already
running, then registers the current folder under that project name in
a small file outside any repo (`~/.mnemo/projects.json`). The first
`memory_add` you make downloads the embedding model automatically
(~500MB, one-time). `memory_add`/`memory_search` work immediately,
same session, no restart.

Want Mnemo available everywhere without installing it repo by repo?
Use `--scope user` instead (Claude Code's default if you omit
`--scope`) — the plugin itself is then available in every project, but
each repo still needs its own `/mnemo:mnemo-register` before memory
tools work there, so nothing is silently connected. Two repos only
ever share the same memories if you deliberately register both under
the *same* project name — that's the one supported way to "join"
projects, and it's opt-in, never automatic.

If `/plugin install mnemo --scope project` says "already installed"
instead of enabling it, that means mnemo is already installed
somewhere else on your machine (e.g. at `user` scope from an earlier
setup) — Claude Code only ever installs a plugin's code once. Use
`/plugin enable mnemo --scope project` instead; that's the command
that actually toggles a scope on for an already-installed plugin.

## Quick start (manual / Cursor / Codex)

```bash
git clone git@github.com:pacheco20222/mnemo.git
cd mnemo
docker compose up -d
uv run mnemo setup --project my-first-project
```

For Claude Code: paste the printed `.mcp.json` block into your repo.
For Cursor: paste the same block into that repo's `.cursor/mcp.json`
instead — identical format, different file, same per-repo scoping. For
Codex, run the command it prints — it looks like this, with your real
path and project name filled in:

```bash
codex mcp add mnemo --env MNEMO_PROJECT=my-first-project -- uv run --directory /absolute/path/to/mnemo mnemo
```

On native Windows, run `uv run mnemo setup --project my-first-project`
from PowerShell and paste the command it prints. The generated command
quotes the project and clone path safely and uses a JSON/TOML-compatible
forward-slash path:

```powershell
codex mcp add mnemo --env 'MNEMO_PROJECT=my-first-project' -- uv run --directory 'C:/absolute/path/to/mnemo' mnemo
```

Run that from anywhere — `--directory` points at this mnemo clone, not
the project you're tracking; `MNEMO_PROJECT` is what fixes the project,
not your current directory. See [docs/INSTALL.md](docs/INSTALL.md) for
the full walkthrough, including the real difference between how Claude
Code and Codex scope projects. If the MCP connects but the first
`memory_add` or `memory_search` fails while FastEmbed loads or downloads
the model, follow the [first-tool troubleshooting steps](docs/INSTALL.md#mcp-connects-but-the-first-memory-tool-fails).

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
