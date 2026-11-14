---
status: living
updated_at: "2026-11-14"
---

# Roadmap — llm-wiki-rag

> **A decomposition, not a promise.** The overall idea broken into incremental steps: what each
> step is, where it comes from, how big it is — or that nobody has looked at it yet — and in which
> order, and parallel lanes, we walk them. **No dates** (except shipped history), **no scores** —
> order is the prioritization. The *solution* for any step lives in its `docs/features/<slug>/`
> spec, not here.

## Destination

The owner can query one personal markdown knowledge base from the CLI, choosing per query whether to get a direct-markdown-read answer or a RAG answer from a vector database, with both modes reading from the same notes folder.

## Steps

| # | Step | Source | Size | Status |
|---|---|---|:---:|---|
| 1 | Scaffold the project skeleton (Python package, CLI entrypoint, test harness, Chroma adapter scaffolding, CI) | `docs/architecture-map.md` §Stack + `docs/features/_scaffold/tasks.json` | S | idea |
| 2 | Query via direct markdown read (Karpathy-style backend: reads notes directly, no embeddings) | `docs/idea-brief.md` §7 | M | idea |
| 3 | Query via RAG against Chroma (embeds notes, manual reindex command, vector-mode query) | `docs/idea-brief.md` §7; `docs/adr/0001-use-python-typer-chroma-stack.md` | M | idea |
| 4 | One CLI command with a per-query mode switch unifying both backends | `docs/idea-brief.md` §7 ("two swappable retrieval backends chosen per query") | S | idea |

## Not yet specified

| Area | What we'd have to learn | Blocks | How it gets sharpened |
|---|---|:---:|---|
| Automatic reindex / staleness detection for the vector index (enhancement past v1's manual command) | Whether file-watch is worth adding once step 3 ships, and what "staleness" should trigger it | — | A recon pass once step 3 is spec'd and manual reindexing has been used for a while |
| Second vector-DB adapter beyond Chroma | Which vector DB (if any) to support next, and whether the current `VectorStore` port shape generalizes to it | — | A recon pass once a concrete second target is named (see Open decisions D2) |
| Agent-initiated writes back into the KB (not scoped today — the CLI only exposes read-only `query` and owner-triggered `reindex`) | Whether an agent should ever be allowed to propose new notes, and if so, how to gate that write so an unreviewed fact can't corrupt the source of truth | — | If this feature is ever picked up: the "2-Phase Commit for agent memory" prepare/confirm pattern (`https://dou.ua/forums/topic/60353/`, cited in `docs/idea-brief.md` §6) is the precedent to revisit |

## Out of scope

- An MCP server or HTTP API interface — owner confirmed CLI-only during `survey`'s intent check (`docs/idea-brief.md` §3).
- Extending the existing installed `llm-wiki` Claude Code plugin instead of building a standalone tool — `docs/idea-brief.md` §5.

## Open decisions

| # | Question | Type | Owner | Blocks |
|---|---|:---:|:---:|:---:|
| D2 | Which second vector database, if any, should be supported after Chroma? | grilling | human | — |

## Decisions so far

- Standalone CLI tool, not an extension of the existing `llm-wiki` plugin → [`docs/idea-brief.md`](idea-brief.md) §5, §7
- Stack: Python 3.12 + Typer + Chroma → [`docs/adr/0001-use-python-typer-chroma-stack.md`](adr/0001-use-python-typer-chroma-stack.md)
- Backends structured as interchangeable ports behind a `KnowledgeBase` core → [`docs/adr/0002-hexagonal-lite-pluggable-backends.md`](adr/0002-hexagonal-lite-pluggable-backends.md)
- Markdown files are the single source of truth; no relational database → [`docs/adr/0003-markdown-as-source-of-truth.md`](adr/0003-markdown-as-source-of-truth.md)
- Vector index reindex stays manual-only for v1 (step 3's own scope is a manual reindex command); automatic/file-watch reindexing is deferred as a post-v1 enhancement, not a blocking unknown → see step 3, `## Not yet specified`

## Dependency graph

```mermaid
flowchart LR
  s1["1 · Scaffold skeleton"] -->|needs a buildable project to build into| s2["2 · Markdown-read query"]
  s2 -->|sequential: build vector backend after markdown backend ships| s3["3 · Vector RAG query (Chroma)"]
  s3 -->|unifies both backends, needs both to exist| s4["4 · Unified CLI mode switch"]
```

## Execution path

| Wave | Steps | Zone per step (why parallel-safe) | Unlocks |
|:---:|---|---|---|
| 1 | 1 | whole repo (new) | 2 |
| 2 | 2 | `src/kb/backends/markdown/` + `src/kb/core/` (new) | 3 |
| 3 | 3 | `src/kb/backends/vector/` + `src/kb/core/` (new) | 4 |
| 4 | 4 | `src/kb/cli/` + `src/kb/core/` (new) | — |

## Shipped

| Step | Shipped | Link |
|---|---|---|
