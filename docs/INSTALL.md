# Installing Mnemo

## Prerequisites

1. **Docker or OrbStack** running locally.
2. **uv** installed ([docs.astral.sh/uv](https://docs.astral.sh/uv/)).

No GPU and no separate embedding service needed — `fastembed` runs
locally on CPU and installs the same way `uv sync` installs every
other Python dependency here. The model itself (~500MB) downloads
automatically, once, the first time you save a memory.

## Option A: Plugin install (recommended for Claude Code)

Inside Claude Code, in whichever repo you want Mnemo available in:

```
/plugin marketplace add pacheco20222/mnemo
/plugin install mnemo
/mnemo:mnemo-register my-project-name
```

`/mnemo:mnemo-register` starts Qdrant (via the plugin's own bundled
`docker-compose.yml`) if it isn't already running, then registers
this folder under that project name in `~/.mnemo/projects.json` — a
file outside any repo, not `.mcp.json`. Nothing gets written into this
repo at all. The first `memory_add` you make afterward downloads the
embedding model automatically (~500MB, one-time).

The MCP server and the checkpoint/resume `SessionStart` hook are both
bundled with the plugin itself, so installing it once (above) already
made both available everywhere — registering a folder just tells
Mnemo which project that folder is. `memory_add`/`memory_search` work
immediately, same session, no restart.

Run `/mnemo:mnemo-register <name>` again in any other repo to add Mnemo
there — same plugin install, no cloning or hand-edited config, ever.
This covers the Claude Code side only; Codex still needs the manual
step in [§4](#4-codex) below, since Codex has no plugin/marketplace or
registry concept of its own.

The rest of this doc (Option B) is the manual path — read it if you're
not using Claude Code, want to see exactly what the plugin command
does under the hood, or ran into something `/mnemo:mnemo-register` didn't
handle.

## Option B: Manual install

### 1. Clone and start the services

```bash
git clone git@github.com:pacheco20222/mnemo.git
cd mnemo
docker compose up -d
```

This starts one Qdrant container — the only always-on process Mnemo
needs. Verify it's up:

```bash
curl -s http://localhost:6333/collections
```

### 2. Get your install path

```bash
uv run mnemo setup
```

This prints a ready-to-paste `.mcp.json` block, an optional
`.claude/settings.json` hook block, and the equivalent `codex mcp add`
command, with your actual clone path already filled in — you don't
need to hand-edit any paths yourself. Re-run it with `--project NAME`
to have the project id filled in too, instead of a placeholder.

### 3. Claude Code

Claude Code scopes MCP servers **per repository**, automatically —
whichever repo's `.mcp.json` is present is what's active for that
session, with zero manual switching.

Copy the block `mnemo setup` printed into a `.mcp.json` file at the
root of whichever repo you want Mnemo available in:

```json
{
  "mcpServers": {
    "mnemo": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/mnemo", "run", "mnemo"],
      "env": {
        "MNEMO_PROJECT": "your-project-name"
      }
    }
  }
}
```

`MNEMO_PROJECT` should be different per repo — it's what keeps one
project's memories from ever showing up in another's. Open (or
restart) a Claude Code session in that repo and `memory_add`/
`memory_search` will be available.

#### Optional: auto-loading checkpoints and documents

Mnemo can automatically surface your latest checkpoint and project
overview at the start of every session, via a Claude Code hook. Add a
`.claude/settings.json` in the same repo:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear",
        "hooks": [
          {
            "type": "command",
            "command": "MNEMO_PROJECT=your-project-name uv run --directory /absolute/path/to/mnemo mnemo-recall"
          }
        ]
      }
    ]
  }
}
```

If a `.claude/settings.json` already exists in that repo, add the
`"hooks"` key alongside whatever's already there rather than replacing
the file.

### 4. Codex

This is genuinely different from Claude Code, not just a syntax
change: **Codex's MCP configuration is global** (`~/.codex/config.toml`),
not scoped per directory. There's no automatic "this repo gets this
project" behavior the way `.mcp.json` gives Claude Code — Codex has to
be told which project applies, every time, by you.

Run the command `mnemo setup` printed:

```bash
codex mcp add mnemo --env MNEMO_PROJECT=your-project-name -- uv run --directory /absolute/path/to/mnemo mnemo
```

This registers **one** globally-visible `mnemo` server fixed to that
one project. Two real options if you work across multiple projects
with Codex:

- **A distinct server name per project** — run `codex mcp add` again
  with a different `NAME` and `MNEMO_PROJECT` each time (e.g.
  `mnemo-projectA`, `mnemo-projectB`). All of them are visible in
  every Codex session at once — nothing hides `mnemo-projectB`'s
  tools while you're working on projectA — so this trades isolation
  for simplicity.
- **A profile per project** — create `~/.codex/<name>.config.toml`
  with just the `mnemo` server's env override for that project, then
  start Codex with `codex -p <name>` when working there. Closer to
  Claude Code's automatic behavior, but only if you remember to pass
  `-p` every session.

Neither is automatic the way Claude Code's per-directory config is —
pick whichever tradeoff fits how you actually use Codex.

### 5. Verify it worked

In a Claude Code or Codex session in your configured repo:

> "Remember that we're using Mnemo to give you persistent memory."

Then in a later session:

> "What do you know about this project?"

If it recalls the note, it's working.
