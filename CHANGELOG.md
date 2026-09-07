# Changelog

## Unreleased

### Fixed
- Native Windows MCP startup no longer imports and initializes FastEmbed before
  the stdio handshake. The first embedding request still performs the existing
  one-time model initialization, while macOS and Linux keep their previous
  startup behavior.
- `mnemo setup` now prints valid JSON paths and a native PowerShell recall hook
  on Windows.

## 2.1.0 — 2026-09-06

### Added
- Native Windows support: `scripts/backup.ps1`, `export_json.ps1`, and
  `daily_backup.ps1` as PowerShell twins of the existing bash scripts
  (same behavior, no shared code). Documented `schtasks` command as
  the `launchd`-plist equivalent for the daily schedule. WSL2 needs no
  code changes — it's Linux underneath, and is now called out in the
  README/docs as a supported path.

## 2.0.1 — 2026-09-05

### Fixed
- Qdrant client connection deferred to first actual tool use instead of at
  module import — a fresh install (Qdrant not started yet) used to crash
  the MCP server before it could even start, surfacing only as a generic
  connection failure with no indication why.
- `/mnemo:mnemo-register` no longer prints a Codex command unconditionally
  — only relevant if you actually use Codex, and Codex has no way to
  invoke this command in the first place.
- README.md and docs/INSTALL.md corrected: the register command's real
  invocable name is `/mnemo:mnemo-register` (plugin-namespaced), not
  `/mnemo-register`.

### Added
- The server now asks before updating the project overview document when
  it notices a relevant change, and periodically asks about saving a note
  — both opt-in, never automatic.

## 2.0.0 — 2026-09-03

### Changed
- **Breaking:** embeddings now run locally via `fastembed` (`nomic-embed-text-v1.5`, ONNX Runtime, CPU-only) instead of Ollama. No GPU, no background service, no separate app to install — `fastembed` installs like any other Python dependency. Existing memories remain valid Qdrant points but are no longer in the same embedding space as anything newly written; no automatic migration is performed.
- `mnemo import`'s chunk size widened from ~1500 to ~6000 tokens (6000→24000 chars), taking advantage of the new backend's 8192-token context window (vs. Ollama's configured 2048).

### Removed
- Ollama and `httpx` as dependencies.

## 1.2.0 — 2026-09-02

### Added
- Local folder-to-project registry (`~/.mnemo/projects.json`) and `memory_register_project` tool / `mnemo register --project X` CLI — lets a repo register itself without writing any file into that repo.
- `.mcp.json` and `hooks/hooks.json` now bundled directly in the plugin — installing it once makes the MCP server and the checkpoint/resume hook available in every session, everywhere. `MNEMO_PROJECT` no longer needs to be baked into either.
- `/mnemo-register <project>` replaces `/mnemo-setup` — same Qdrant/Ollama checks, but registers the folder instead of writing `.mcp.json` into it.

### Fixed
- `server.py` no longer resolves the project once at import time — it's now resolved per tool call, so the server always starts even in a brand-new, unregistered folder (previously it would crash before a registration tool could ever run there).

## 1.1.0 — 2026-09-02

### Added
- Claude Code plugin packaging (`.claude-plugin/plugin.json` + `marketplace.json`) — installable via `/plugin marketplace add pacheco20222/mnemo` then `/plugin install mnemo`, no cloning required for the Claude Code side.
- `/mnemo-setup <project>` command — starts Qdrant if it isn't running, checks for the `nomic-embed-text` model, and writes/merges this repo's `.mcp.json` and (optionally) the checkpoint/resume `SessionStart` hook. Replaces copy-pasting `mnemo setup`'s terminal output by hand.
- `mnemo setup` now also prints the `SessionStart` hook block (previously only documented manually in INSTALL.md, not printed).

## 1.0.0 — 2026-09-02

First packaged release. Everything below was built and proven across
five real repositories before this release was cut.

### Added
- Core memory: `memory_add`, `memory_search`, hard project isolation via `MNEMO_PROJECT`.
- `memory_search_global` — explicit cross-project search.
- `mnemo import` — bulk-load a file into a project's memory, with paragraph-aware chunking to stay under the embedding model's context window.
- Checkpoint/resume — `memory_add(type="checkpoint")` + automatic recall via a `SessionStart` hook.
- Named documents — `memory_set_document`/`memory_get_document`, replace-in-place by slug, with the project overview auto-loading every session.
- `mnemo graph` — a real embedding-similarity graph of your memories, rendered locally.
- `mnemo setup` — prints ready-to-paste Claude Code and Codex configuration with the real install path filled in.
- Scheduled backups (`launchd`) with retention, plus a flat JSON export.
