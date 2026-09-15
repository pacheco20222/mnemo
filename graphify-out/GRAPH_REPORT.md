# Graph Report - mnemo  (2026-09-14)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 185 nodes · 297 edges · 19 communities (7 shown, 5 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `797687f4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 1
- Community 2
- Community 3
- Community 4
- Community 6
- Community 7
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15

## God Nodes (most connected - your core abstractions)
1. `_vector()` - 13 edges
2. `main()` - 9 edges
3. `main()` - 9 edges
4. `embed_text()` - 8 edges
5. `_get_client()` - 8 edges
6. `get_client()` - 7 edges
7. `get_project()` - 7 edges
8. `memory_add()` - 7 edges
9. `memory_set_document()` - 7 edges
10. `lookup()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `test_embed_text_differs_for_different_input()` --calls--> `embed_text()`  [INFERRED]
  tests/test_embeddings.py → src/mnemo/embeddings.py
- `test_embed_text_returns_768_floats()` --calls--> `embed_text()`  [INFERRED]
  tests/test_embeddings.py → src/mnemo/embeddings.py
- `get_project()` --calls--> `lookup()`  [EXTRACTED]
  src/mnemo/config.py → src/mnemo/registry.py
- `main()` --calls--> `lookup()`  [EXTRACTED]
  src/mnemo/recall.py → src/mnemo/registry.py
- `main()` --calls--> `register()`  [EXTRACTED]
  src/mnemo/register_cli.py → src/mnemo/registry.py

## Import Cycles
- None detected.

## Communities (19 total, 5 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (16): client(), collection(), fixture, test_add_and_search_scoped_by_project(), test_get_all_with_vectors_filters_by_project(), test_get_all_with_vectors_returns_vectors(), test_get_latest_filters_by_type(), test_get_latest_returns_newest_by_created_at() (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (17): Exception, Path, _load(), lookup(), Raised when the registry file exists but can't be parsed as JSON., register(), registry_path(), RegistryError (+9 more)

### Community 3 - "Community 3"
Cohesion: 0.23
Nodes (16): QdrantClient, _chunk_text(), main(), latest_checkpoint(), main(), overview_document(), add_memory(), _document_id() (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.23
Nodes (13): get_project(), validate_type(), embed_text(), _get_client(), memory_add(), memory_get_document(), memory_register_project(), memory_search() (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.23
Nodes (10): main(), _build_graph_data(), _cosine(), main(), _render_html(), main(), main(), main() (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.23
Nodes (10): parametrize, skipif, _codex_command(), _printed_json_documents(), test_powershell_quote_doubles_single_quotes_only(), test_powershell_quote_round_trips_via_encoded_command(), test_setup_json_round_trips_special_project_on_both_platforms(), test_setup_prints_mcp_json_and_codex_command() (+2 more)

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (7): description, name, owner, name, url, plugins, $schema

## Knowledge Gaps
- **11 isolated node(s):** `description`, `name`, `name`, `url`, `plugins` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 83 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 6` to `Community 2`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 6` to `Community 2`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Path` (e.g. with `main()` and `main()`) actually correct?**
  _`Path` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `description`, `name`, `name` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `Community 5` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._