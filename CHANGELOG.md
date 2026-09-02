# Changelog

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
