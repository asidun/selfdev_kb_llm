---
status: Accepted
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "N/A — greenfield foundation, not a feature"
ticket: "N/A"
---

# 0001 — Use Python + Typer + Chroma as the initial stack

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Andrii Sidun (owner), during `survey` greenfield foundation session

## Context

The project (`docs/idea-brief.md`) is a personal CLI tool exposing one knowledge-base interface
over two swappable retrieval backends: direct markdown reads and RAG against a pluggable vector
database. A concrete language/runtime and a first concrete vector-DB target must be fixed before
any code can be scaffolded.

## Decision drivers

- Owner-reported goal: the vector-DB side must be pluggable ("any vector database") — the stack
  must make writing additional adapters straightforward (idea-brief §7).
- Single-user CLI tool, no deadline, exploratory (idea-brief §4) — favors the ecosystem with the
  richest off-the-shelf embedding/vector-DB tooling over raw performance.
- CLI-only interface, no HTTP server (confirmed during `survey` intent confirmation).

## Considered options

1. **Python + Typer + Chroma** — Python has the deepest ecosystem of embedding/vector-DB client
   libraries (Chroma, Qdrant, Pinecone, Weaviate clients all exist as Python packages), Typer is a
   lightweight idiomatic CLI framework, Chroma runs embedded/local with zero external services.
2. **Go + Cobra + a Go vector-DB client** — faster single binary, but far fewer vector-DB client
   libraries exist in Go; several targets would need raw HTTP calls instead of maintained SDKs.
3. **Node/TypeScript + a vector-DB SDK** — reasonable SDK coverage, but weaker ecosystem for local
   embedded vector stores and markdown-note tooling than Python's.

## Decision outcome

**Chosen:** Option 1 (Python + Typer + Chroma). Python's vector-DB client coverage directly serves
the pluggability driver, and Chroma's embedded/local mode needs no extra infrastructure for a
single-user personal tool.

## Consequences

**Positive**
- Broadest selection of vector-DB client SDKs to add as future `VectorStore` adapters.
- Chroma requires no separate server process to run locally.

**Negative**
- Python CLI startup is slower than a compiled binary (Go/Rust) — acceptable for a personal tool
  invoked interactively, not for high-frequency scripted calls.

**Neutral**
- Switching the vector-DB adapter later (e.g. to Qdrant) is a new adapter behind the existing
  `VectorStore` port, not a stack change; switching the *language* later would be a rewrite.

## Links

- Spec: `docs/idea-brief.md`
- SAD: `docs/architecture-map.md` §Stack
- Related ADR: [[0002-hexagonal-lite-pluggable-backends]]
