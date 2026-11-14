---
status: Accepted
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "N/A — greenfield foundation, not a feature"
ticket: "N/A"
---

# 0002 — Structure backends as interchangeable ports behind a KnowledgeBase core

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Andrii Sidun (owner), during `survey` greenfield foundation session

## Context

The owner wants per-query backend switching (idea-brief §7): the same markdown content must be
queryable either by direct file read/synthesis or by RAG against a vector DB, chosen at query
time. The module structure must make that switch a parameter, not a rewrite.

## Decision drivers

- Owner-decided: switching is per-query, not per-deployment (idea-brief §7: "two swappable
  retrieval backends chosen per query").
- Owner-reported pluggability goal: more vector DBs must be addable later without touching the
  CLI or the markdown backend.

## Considered options

1. **Hexagonal-lite: a `KnowledgeBase` core that dispatches to a `Backend` port, with `markdown`
   and `vector` as two interchangeable implementations** — the CLI never talks to a backend
   directly, only to the core.
2. **Two independent CLI subcommands, one per backend, no shared core** — simpler to write
   initially, but duplicates query-parsing/output logic and makes "switch per query" an
   if/else in the CLI layer instead of a domain concern.
3. **A single backend class with an internal `if mode == "vector"` branch** — least structure,
   but adding a third backend (a second vector DB) means branching logic growing unbounded in one
   file instead of a new adapter.

## Decision outcome

**Chosen:** Option 1. A shared `Backend` port keeps the CLI thin and makes "add a vector DB" or
"add a third retrieval mode" a matter of writing one new adapter, not touching existing code.

## Consequences

**Positive**
- New vector-DB adapters are additive (`backends/vector/<new_db>.py` implementing `VectorStore`),
  no changes needed to `core` or `cli`.
- The markdown backend and vector backend stay testable in isolation.

**Negative**
- More upfront structure (ports + adapters) than a two-subcommand script, which is overkill if the
  project never grows past Chroma + markdown.

**Neutral**
- The `VectorStore` port's exact method signatures are a `design`-time decision, not fixed here.

## Links

- Spec: `docs/idea-brief.md`
- SAD: `docs/architecture-map.md` §Module inventory
- Related ADR: [[0001-use-python-typer-chroma-stack]], [[0003-markdown-as-source-of-truth]]
