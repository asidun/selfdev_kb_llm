---
status: Draft
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "S"
---

# Data model — markdown-query-backend

## No relational/vector schema change

This feature introduces **no datastore, no table, no vector collection, and no migration** —
confirmed by `architecture-map.md` (`migration_tool: ""`, "no relational DB; the vector backend's
own store is the persistence") and `sad.md` §2/§4/§8 (markdown files on local disk remain the sole
source of truth; no new datastore, no caching, no index; ADR 0003). The markdown backend re-scans
the notes root on every call (AC-09) — there is nothing to persist across queries and therefore
nothing to migrate.

Per the skill's "no schema change" outcome: this is a legitimate result, not a gap. **Zero
migration files are staged** under `docs/features/markdown-query-backend/migrations/` (the
directory is intentionally not created).

What follows documents the feature's **in-process data shapes** instead (the entities `sad.md` §5
names: `Note`, the shared `Answer` result) so downstream `api` has a typed source to derive the
CLI/library contract from, and so a future reader can see what *would* need a migration if this
backend ever grew a cache or index.

## In-process data shapes (not DB tables)

### `Note` (`src/kb/backends/markdown/note.py`, new)

Parsed fresh from a single `.md` file on every query; never persisted.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `path` | `Path` | relative to notes root | identity for ranking tiebreak (AC-02b) and `sources` |
| `frontmatter` | `dict[str, Any]` \| `None` | `None` when missing/unparsable → note is skipped | parsed via PyYAML (ADR-0002); expected keys `title`, `summary`, `tags` |
| `body` | `str` | — | raw markdown body, post-frontmatter-delimiter |
| `skip_reason` | `str` \| `None` | `None` when healthy | set for unreadable file, missing/malformed frontmatter (AC-06), or an escaping/looping symlink (AC-08) |

**Aggregate root:** root — one `Note` per `.md` file; no parent/child relationship between notes.
**Access pattern:** `MarkdownBackend.query` iterates every `Note` under the notes root once per
call (`Path.rglob("*.md")`, sad.md §5) — no index exists to serve this scan, by design (non-goal:
no reindexing/caching between queries).

### `Answer` (`src/kb/core/knowledge_base.py`, existing — unchanged shape)

Shared across both backends behind the `Backend` protocol (ADR 0002, repo-root). This feature does
**not** add a field to it: sad.md §1's decision override narrows spec §1's "extend `Answer` with a
skipped-note count" to appending that count as plain text inside `.text` (spec §8 OQ3's own
default), leaving the dataclass's 2-field shape untouched for v1.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `text` | `str` | — | ranked, excerpted matches; skipped-note count appended as plain text (sad.md §8 "Result surfacing") |
| `sources` | `list[str]` | — | matching notes' paths, in rank order |

**Access pattern:** returned once per `MarkdownBackend.query(text)` call; never stored.

## Indexes

N/A — no datastore exists for this feature to index. The backend's only "index" is the filesystem
walk itself (`Path.rglob("*.md")`), which is not a persisted structure and carries no index
candidate from the sequence diagrams (sad.md §6): every flow reads fresh from `Notes root`, none
reads from a store this feature controls.

## Test fixtures

<!-- Matches the repo's existing fixture convention (tests/backends/test_vector_backend.py): plain
pytest tmp_path-built directories, no factory/builder library. NOT written to migrations/. -->

- `tmp_path`-built notes root with a healthy note — `title`/`summary`/`tags` frontmatter + body —
  for the happy-path match/rank/excerpt assertions (AC-01, AC-02, AC-03).
- A second healthy note whose frontmatter alone satisfies every significant word, to assert the
  Frontmatter-complete vs. body-completed rank split (AC-02) and the path-order tiebreak (AC-02b).
- A malformed note — missing frontmatter delimiter, or invalid YAML — to assert skip accounting
  (AC-06) and that healthy notes still match around it (AC-07).
- A note under a dot-prefixed directory (e.g. `.obsidian/`) and a non-`.md` file, to assert neither
  is counted toward matches or the skipped total (AC-10).
- A symlink inside the notes root resolving outside it, and a self-looping symlink, to assert
  AC-08's reject-and-count behavior; a symlink resolving to a target still inside the notes root,
  to assert it is followed normally.
- A notes root path that does not exist, to assert `NotesRootError` (ADR-0001, AC-04b) instead of
  the old soft Answer-embedded message — `tests/test_smoke.py`'s
  `test_query_markdown_mode_on_missing_notes_root` must be updated in the same PR (sad.md §11 risk
  row), since it currently asserts the superseded `exit_code == 0` behavior.
- A blank/whitespace-only query string, to assert `BlankQueryError` (AC-05).
- No real-looking PII in any fixture note content — generic placeholder titles/bodies only.
