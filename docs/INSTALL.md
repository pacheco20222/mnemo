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
change: the `codex mcp add` command writes a **global** entry to
`~/.codex/config.toml`. There's no automatic "this repo gets this project"
behavior from that global entry the way `.mcp.json` gives Claude Code —
the configured `MNEMO_PROJECT` selects the project for every session that
loads that server. Codex also supports project-scoped `.codex/config.toml`
files in trusted projects, but the command below uses the simpler global
setup.

Run the command `mnemo setup` printed:

```bash
codex mcp add mnemo --env MNEMO_PROJECT=your-project-name -- uv run --directory /absolute/path/to/mnemo mnemo
```

This is a one-time registration, not a command you run before every Codex
session. Verify what Codex stored, then start a new session:

```bash
codex mcp get mnemo
codex mcp list
codex
```

Two things that trip people up here: `--directory` points at wherever
you cloned **mnemo itself**, not the project you're tracking — that's
just so `uv` can find mnemo's own code to run, and has nothing to do
with project scoping. You don't need to run this command from inside
the target repo (`your-project-name`'s folder) either — `MNEMO_PROJECT`
fixes the project for every call this server makes, completely
independent of your current directory, unlike Claude Code's
cwd-based registry.

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

If `mnemo` is already registered and you want that name to point to a
different project, replace the entry and restart Codex:

```bash
codex mcp remove mnemo
codex mcp add mnemo --env MNEMO_PROJECT=my-other-project -- uv run --directory /absolute/path/to/mnemo mnemo
```

### 5. Running `mnemo`'s other commands (import, graph)

`mnemo import` and `mnemo graph` aren't called by Claude Code or
Codex — you run these yourself, directly. Like every `uv run mnemo`
invocation, `uv` needs to find mnemo's own code, either by cwd or by
`--directory`:

```bash
cd /path/to/mnemo   # wherever you cloned it
uv run mnemo graph --project your-project-name
uv run mnemo import notes.md --project your-project-name --type note
```

or from anywhere else:

```bash
uv run --directory /path/to/mnemo mnemo graph --project your-project-name
```

Real gotcha with `--directory`: it changes the command's working
directory to wherever you cloned mnemo, not wherever you actually are
— so a relative file path passed to `mnemo import` (e.g. `notes.md`)
resolves against **mnemo's** folder, not yours, unless you `cd` into
mnemo first (first example above) or pass an absolute path to the
file instead.

`mnemo graph` without `--project` graphs every project's memories
together, not just one. It needs at least 2 memories to draw anything,
writes a self-contained HTML file (`--out path.html` to control
where — defaults to your current directory), and opens it in your
default browser automatically.

### 6. Windows

Two real options, same as always — pick one, don't mix them for the
same install:

**WSL2** — this is just Linux underneath. Everything above (Option A
or B, Claude Code or Codex) works completely unmodified inside a WSL2
distro. If you're already comfortable with WSL2, this is the easy path
and there's nothing else in this section for you.

**Native Windows (PowerShell/cmd, no WSL)** — Docker Desktop, `uv`,
and `docker compose` all work natively. From PowerShell, the complete
setup is:

```powershell
git clone https://github.com/pacheco20222/mnemo.git
Set-Location mnemo
docker compose up -d
uv run mnemo setup --project my-first-project

codex mcp add mnemo --env "MNEMO_PROJECT=my-first-project" -- uv run --directory "C:/absolute/path/to/mnemo" mnemo
codex mcp get mnemo

Set-Location "C:/path/to/my-first-project"
codex
```

Replace `C:/absolute/path/to/mnemo` with the folder where you cloned Mnemo.
`--directory` points to the Mnemo clone, not the application project you
want it to remember. `MNEMO_PROJECT` is the memory namespace for that
application. Run `codex mcp add` once, then start or restart Codex.

Windows-specific details:

- Paths in `.mcp.json`, `~/.codex/config.toml`, or the `codex mcp add`
  command need either forward slashes or doubled backslashes — both
  `C:/Users/you/mnemo` and `C:\\Users\\you\\mnemo` are valid; a single
  backslash isn't, in JSON or TOML.
- The backup scripts are PowerShell twins (`backup.ps1`,
  `export_json.ps1`, `daily_backup.ps1` in `scripts/`) — same
  behavior as the `.sh` versions, same env vars
  (`MNEMO_QDRANT_URL`, `MNEMO_COLLECTION`). Run them directly:
  ```powershell
  .\scripts\daily_backup.ps1
  ```
  For the daily schedule (replaces `launchd` on macOS), one command —
  no separate task-definition file needed:
  ```
  schtasks /create /tn "MnemoDailyBackup" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"C:\path\to\mnemo\scripts\daily_backup.ps1\"" /sc daily /st 03:00
  ```
  `-ExecutionPolicy Bypass` is scoped to just this scheduled task —
  it doesn't change your system-wide PowerShell execution policy.

#### Windows Codex startup and troubleshooting

Mnemo defers FastEmbed import and model initialization until the first
embedding request on native Windows. This lets the MCP server answer Codex's
`initialize` request before the one-time model download begins. The first
`memory_add` or `memory_search` can still take longer while the model is
downloaded and loaded; later requests use the cached model.

If Codex reports that Mnemo failed during the `initialize` response:

1. Confirm the stored command and project:
   ```powershell
   codex mcp get mnemo
   codex mcp list
   ```
2. Confirm Qdrant is running from the Mnemo clone:
   ```powershell
   docker compose ps
   ```
3. Make sure the stored `--directory` uses the real Mnemo clone path with
   forward slashes, such as `C:/Users/you/code/mnemo`.
4. Remove and recreate a stale entry, then restart Codex:
   ```powershell
   codex mcp remove mnemo
   codex mcp add mnemo --env "MNEMO_PROJECT=my-project" -- uv run --directory "C:/Users/you/code/mnemo" mnemo
   ```

`mnemo import` and `mnemo graph` (§5 above) need nothing extra on
Windows — both are plain, cross-platform Python: `mnemo graph`'s
browser-opening and `mnemo import`'s file reading have no OS-specific
code path to work around. The same `cd` / `--directory` rule from §5
applies exactly as written.

### 7. Verify it worked

This is just seeding one test memory so there's something to recall —
on a fresh install the collection is empty, so say anything you like.
In a Claude Code or Codex session in your configured repo:

> "Remember that we're using Mnemo to give you persistent memory."

Then in a later session:

> "What do you know about this project?"

If it recalls the note, it's working.
