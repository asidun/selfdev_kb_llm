---
status: Accepted
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "N/A — greenfield foundation, not a feature"
ticket: "N/A"
---

# 0003 — Treat markdown files as the single source of truth; no relational database

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Andrii Sidun (owner), during `survey` greenfield foundation session

## Context

Both retrieval backends must answer from the same content. The project needs a persistence/ID
strategy decided now, since it is hard to change once notes and a vector index both exist.

## Decision drivers

- Owner-reported goal: no single existing wiki yet, starting from empty (idea-brief, "Existing
  data") — no legacy storage format to preserve.
- Owner-reported risk already logged in idea-brief §7: the vector index must stay in sync with one
  canonical content store — picking markdown-as-source-of-truth settles which side is canonical.

## Considered options

1. **Markdown files on disk are the only source of truth; the vector DB is a derived, rebuildable
   index over them** — content-hash-based chunk IDs so re-ingesting unchanged notes is a no-op.
2. **A relational/document database stores notes; markdown is just an export/import format** —
   adds a datastore the owner didn't ask for, and duplicates what plain files already do well.
3. **The vector DB is the source of truth; markdown files are generated from it** — breaks the
   git-diffable, human-editable markdown workflow central to the Karpathy-style backend.

## Decision outcome

**Chosen:** Option 1. Markdown stays authoritative and human-editable; the vector index is always
re-derivable from it, which also answers "how do the two backends stay consistent" — they both
read from (or are built from) the same files.

## Consequences

**Positive**
- No relational database or migration tooling needed for a single-user CLI tool.
- The vector index can always be deleted and rebuilt from the markdown source — no data loss risk
  on the vector side.

**Negative**
- Reindexing cost grows with note count; the exact reindex trigger (on-demand command vs.
  file-watch) is still open (tracked as an open question, not resolved by this ADR).

**Neutral**
- Content-hash chunk IDs make the index idempotent but don't by themselves solve staleness
  detection (knowing *when* to reindex) — left to `design`.

## Links

- Spec: `docs/idea-brief.md`
- SAD: `docs/architecture-map.md` §Datastores, §Constraints & known tech-debt
- Related ADR: [[0001-use-python-typer-chroma-stack]], [[0002-hexagonal-lite-pluggable-backends]]
