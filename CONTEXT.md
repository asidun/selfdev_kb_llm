---
status: Living
updated_at: "2026-11-14"
---

# Domain Context — llm-wiki-rag

## Glossary

- Backend — one of the interchangeable retrieval implementations (`markdown` or `vector`) that answers a query behind the shared `Backend` protocol. NOT a database — a backend is a retrieval strategy, not a storage engine.
- Note — one markdown file under the notes root; the atomic unit of content either backend reads or indexes. NOT a hosted wiki page — a note is a local file, not a rendered page in a hosted product.
- Notes root — the filesystem folder holding all notes; the single source of truth both backends read from. NOT the vector index — the vector index is a derived, rebuildable cache over the notes root, not the source of truth.
- Owner — the single person who runs the kb CLI and owns the notes; the only actor in this system. NOT a generic multi-tenant "user" — this is a personal single-user tool, there is no multi-user concept.
- Query mode — the per-call selector (`markdown` or `vector`) naming which backend answers a given query. NOT the backend itself — the mode is the parameter value; the backend is the implementation it selects.
