# CLAUDE.md — llm-wiki-rag (kb)

Personal CLI knowledge-base tool: one `KnowledgeBase` core dispatching per-query to a `markdown`
backend (direct file read, Karpathy-style, no embeddings) or a `vector` backend (RAG via Chroma).
Both read from the same markdown notes folder. CLI-only — no HTTP/MCP server.

See `docs/architecture-map.md` for the full foundation and `docs/adr/` for the irreversible picks.

## Build / test / lint

- Install: `pip install -e ".[vector,dev]"`
- Test: `pytest`
- Lint: `ruff check . && black --check .`

## Module layout

- `src/kb/cli/` — Typer commands (`query`, `reindex`); parses `--mode`, never talks to a backend directly
- `src/kb/core/` — `KnowledgeBase` domain type; routes a query to the selected backend behind the `Backend` protocol
- `src/kb/backends/markdown/` — direct markdown-file read + excerpt matching
- `src/kb/backends/vector/` — embeds notes via Chroma's default local embedder (ONNX, all-MiniLM-L6-v2, no network), indexes/queries via `ChromaStore`
- `src/kb/config/` — notes root path, backend defaults, vector-DB settings

## Conventions

- **Wiring:** backends implement the `Backend` protocol (`query(text) -> Answer`); `core` resolves by name — plain constructor injection, no DI framework.
- **Errors:** a single `KbError` hierarchy (`src/kb/core/knowledge_base.py`); the CLI catches at the top and prints one line + exits non-zero.
- **IDs:** content-hash (SHA256 of note path + content) as the chunk ID for the vector backend — re-ingesting unchanged notes is a no-op.
- **Persistence:** markdown files on disk are the source of truth; `ChromaStore` wraps Chroma — no relational DB, no migrations.
- **Tests:** pytest; unit tests per module, integration tests exercise a real temp-dir Chroma instance — never mock the vector DB.
- **Inter-module comms:** direct in-process calls only — single-process CLI, no network between modules.

## Adding a backend

A new vector DB implements the same shape as `ChromaStore` (`reindex(notes_root) -> int`,
`query(text) -> list[VectorResult]`) and is wired into `VectorBackend` — no changes to `core` or `cli`.
