# Changelog

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
