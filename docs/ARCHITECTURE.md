# Architecture

## Stack

| Layer | Choice | Why |
|---|---|---|
| Vector store | [Qdrant](https://qdrant.tech/) (Docker) | Single container, stores vectors + metadata together, free |
| Embeddings | `nomic-embed-text` via [Ollama](https://ollama.com/) | Local, free, no external API call ever |
| MCP server | [FastMCP](https://gofastmcp.com/) (Python), stdio transport | No network exposure, low boilerplate |

Qdrant is the only always-on process. The MCP server itself is spawned
as a subprocess per session by Claude Code or Codex — it is not a
background daemon.

## Data model

Every memory is one Qdrant point:

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Random for regular memories; deterministic (`uuid5(project:slug)`) for named documents |
| `vector` | float[768] | `nomic-embed-text` embedding of `content` |
| `project` | string | Required on every point — the hard isolation boundary |
| `type` | string | `decision` \| `architecture` \| `bug` \| `todo` \| `note` \| `checkpoint` |
| `content` | string | The memory text |
| `created_at` | ISO8601 UTC | |
| `source` | string, optional | File path for `mnemo import`-created memories |
| `slug` | string, optional | Present only on named documents |
| `updated_at` | ISO8601 UTC, optional | Present only on named documents, refreshed on every `memory_set_document` call |

## Project isolation

Every tool except `memory_search_global` is implicitly scoped to
`MNEMO_PROJECT` (read once, at server startup, from the environment —
fail-closed if unset). No tool takes a `project` parameter, so there's
no way to accidentally read or write another project's memories from
inside a session. `memory_search_global` is the one deliberate,
explicitly-named exception — isolation by tool choice, not a per-call
permission check.

## Tools

- **`memory_add(content: str, type: str) -> dict`** — always creates a new memory. `type` must be one of the five listed above, or `checkpoint`.
- **`memory_search(query: str, type: str | None = None, k: int = 5) -> list[dict]`** — semantic search, scoped to the current project.
- **`memory_search_global(query: str, type: str | None = None, k: int = 5) -> list[dict]`** — the same search, across every project. Use only for an explicitly cross-project ask.
- **`memory_set_document(slug: str, content: str, type: str) -> dict`** — replace-in-place, keyed by `(project, slug)`. Use for content that should supersede its previous version — a project overview, a running dev log — not accumulate.
- **`memory_get_document(slug: str) -> dict | None`** — exact lookup by slug, no embedding call involved.

## Checkpoint / resume

`memory_add(..., type="checkpoint")` is a normal memory with one
convention: the server's own `instructions` field tells the connected
model to use it when asked to checkpoint, and to write it so someone
with zero memory of the conversation could resume from it alone.
Recall is a `SessionStart` hook running `mnemo-recall`, which does a
direct, chronological (`order_by`, not semantic search) Qdrant lookup
for the newest checkpoint — no embedding call on the read path.

## Named documents auto-load

By convention (not enforced in code), a project's own overview
document uses the project's own id as its `slug`. The same
`SessionStart` hook that recalls the latest checkpoint also looks up
that one document and prints it, so both show up automatically at the
start of every session.

## `mnemo import`

`mnemo import <file> --project X --type Y` splits the file on
paragraph breaks, grouping consecutive paragraphs up to ~6000
characters (~1500 tokens) per chunk — comfortably under
`nomic-embed-text`'s 2048-token context window, so nothing silently
gets truncated in the embedding. Multi-chunk files are tagged via
`source`: `"<file> (chunk 2/5)"`.

## `mnemo graph`

`mnemo graph [--project NAME] [--out PATH]` computes real pairwise
cosine similarity between every matching memory's embedding, keeps
each node's top-3 nearest neighbors as edges, and renders it as a
self-contained HTML file (dark, force-directed, Canvas-rendered) that
opens in your browser. Not decorative — the connections are the
model's own actual similarity judgments.

## `mnemo setup`

Resolves its own install location at runtime (`Path(__file__).resolve().parents[2]`)
and prints ready-to-paste Claude Code and Codex configuration —
nothing to hand-edit, no assumed path.

## Backups

`scripts/backup.sh` creates a Qdrant snapshot; `scripts/export_json.sh`
exports every memory as a flat, human-readable JSON file (no vectors).
Both prune to the newest 14. `scripts/daily_backup.sh` runs both in
sequence — see `scripts/com.mnemo.dailybackup.plist` for the macOS
`launchd` schedule (3 AM daily).
