---
status: Draft
owner: "Andrii Sidun"
updated_at: "2026-11-14"
depth: "medium"
---

# Idea brief — llm-wiki-rag

## 1. Raw idea

Розробити програму яка буде працювати або з локальним llm wiki з MD файлів використовуючи підхід Андрія карпатий або зможе працювати з будь-якою векторною базою як rag. основна ідея програми що це база знань яку може використовувати LLM наприклад клод. ось приклад того що я хочу зробити https://dou.ua/forums/topic/60353/?from=comment-digest_topic_tech&utm_source=digest-comments&utm_medium=email&utm_campaign=13112026 але хочу мати можливість переключатись llm-wiki і rag

## 2. Problem

Owner wants one knowledge-base tool usable across different LLM clients/tools, not locked to Claude Code. Direct-markdown-read ("Karpathy approach") works well inside Claude Code but is Claude-Code-specific; other LLM tools/clients typically expect a vector-DB/RAG-style retrieval interface instead. Owner-reported: the goal is a knowledge base that can switch its backend (plain-markdown read vs. any vector DB as RAG) depending on which LLM/client is consuming it, rather than maintaining two separate incompatible knowledge bases.

## 3. Users

Single user: the owner (Andrii Sidun), personal use. Owner-decided: accessed via CLI only (not an MCP server, not a local HTTP API) — narrowed from the original "CLI/local API" framing during the `survey` intent confirmation, where the owner chose "CLI only" explicitly over "CLI + local API" and "local API only". Called directly as a subprocess from scripts or other programs when querying the knowledge base, independent of which LLM/client consumes the results.

## 4. Why now

No trigger established. Owner-confirmed: exploratory personal project, no deadline or external pressure.

## 5. Out of scope

- Extending the existing `llm-wiki` Claude Code plugin to add a vector-DB backend. Owner-decided: this is to be a new standalone application/tool, not a plugin extension — reason: owner wants a program usable outside Claude Code's plugin system, independent of that existing implementation.

## 6. Risks

Compact evidence ledger:

| Claim/question | Class | Source/origin | Finding/limit |
|---|---|---|---|
| Referenced DOU forum post describes a markdown-based "WikiMemory" system with a prepare/confirm human-approval gate, rejecting vector DBs in favor of git-reviewable Markdown files | source-verified | https://dou.ua/forums/topic/60353/ (fetched 2026-11-14) | Article does not mention "Andrej Karpathy's approach" by that name; that framing came from the owner, not the source. Limitation: fetched via automated summary, not full manual read. |
| "Karpathy's LLM wiki approach" = plain markdown notes folder (consistent per-note structure: title/summary/tags/content, folders like `inbox/`, `projects/`, `reference/`) read directly by Claude Code via natural-language queries, no embeddings by default; vector/semantic search suggested only as an optional scaling layer past "a few hundred notes" | source-verified | https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-knowledge-base-claude-code (fetched 2026-11-14) | Automated summary, not full manual read. |
| An installed Claude Code plugin `llm-wiki` (v2.9.0) already implements this markdown-wiki mode: commands `wiki-init`, `wiki-ingest`, `wiki-query`, `wiki-lint`, `wiki-log` and agents `wiki-ingestor`, `wiki-librarian`, `wiki-linter` | source-verified | local plugin cache: `.claude\plugins\cache\claude-code-skills\llm-wiki\2.9.0` (inspected 2026-11-14) | Directory listing only; internal logic of each skill/agent not read. |

## 7. Recommendation

Owner-accepted direction: build a new standalone CLI/local-API tool, starting from an empty markdown note collection, that exposes a single knowledge-base interface over two swappable retrieval backends chosen per query: (a) direct markdown-file read/synthesis in the style described for Karpathy's approach (plain MD files, consistent note structure, no embeddings), and (b) RAG retrieval against a pluggable vector database. Single user (owner), personal/exploratory project with no deadline.

Major tradeoff: supporting per-query backend switching over the same underlying markdown source means both backends must stay in sync with one canonical content store (indexing the vector DB from the same markdown files) — this adds sync/indexing complexity compared to picking one backend permanently.

Rejected alternative: extending the existing installed `llm-wiki` Claude Code plugin instead of building new (§5) — rejected because the owner wants a standalone tool usable outside the Claude Code plugin system, not an in-plugin extension.

Outcome: **ready-for-specify**. No blocking unknowns remain for the interview's own scope; backend abstraction design, vector-DB choice(s), and indexing/sync mechanics are specify/design-level decisions, not interview-level.

## 8. Open questions

- Which vector database(s) to actually support first (owner said "any," but an initial implementation needs at least one concrete target) — nonblocking for interview, belongs to specify/design — owner: Andrii Sidun.
- How the vector-DB index stays in sync with the markdown source of truth (re-embed on file change? manual reindex command?) — nonblocking for interview, belongs to design — owner: Andrii Sidun.
