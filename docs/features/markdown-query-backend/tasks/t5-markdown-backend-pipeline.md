---
id: T5
title: "Wire MarkdownBackend.query() to the real scan-parse-match-rank-excerpt pipeline"
layer: "app"
deps: ["T2", "T3", "T4"]
blocks: ["T6", "T7", "T8", "T9"]
acs: ["AC-04", "AC-07", "AC-09"]
files_hint: ["src/kb/backends/markdown/backend.py"]
owner: "Andrii Sidun"
estimate: "M"
context_budget: "M"
status: "todo"
step: ""
---

# T5 — Wire MarkdownBackend.query() to the real scan-parse-match-rank-excerpt pipeline

## Place in the sequence

- **Blocked by:** T2 — Add NotesRootError/BlankQueryError, T3 — Implement Note parsing, T4 — Implement matching/ranking/excerpting · **Blocks:** T6 — Update test_smoke.py, T7 — Integration tests (match/rank/no-match), T8 — Integration tests (skip/symlink) · **Wave:** 3.
- **Lane:** own lane — only file touched is `src/kb/backends/markdown/backend.py`. This is the orchestration task: it replaces the existing placeholder stub wholesale.

## Why (user story)

> **As an** Owner
> **I want** a clear "no matching notes" answer when nothing fits my query
> **So that** I know the knowledge base genuinely has nothing on the topic, instead of getting a confusing error
>
> — `spec.md §4, US-04, verbatim` · full text: [spec.md](../spec.md)

This task wires the scan → parse (T3) → match/rank/excerpt (T4) pipeline together in `backend.py`, replacing today's literal substring-scan stub and raising the new error types (T2) instead of returning them as soft text.

## Inlined context

> `backend.py` <MarkdownBackend.query(text) -> Answer; wires the pipeline; raises NotesRootError>
>
> `backend.py` never reads file content directly — `note.py` owns all filesystem/parsing concerns (including the symlink check from AC-08), and `excerpt.py` owns everything that is purely text-in/text-out.
>
> — `sad.md §5, Internal decomposition, verbatim` · full text: [sad.md](../sad.md)

Current stub (verified in repo, `src/kb/backends/markdown/backend.py`) to be replaced:
```python
def query(self, text: str) -> Answer:
    if not self._notes_root.exists():
        return Answer(text=f"notes root {self._notes_root} does not exist", sources=[])
    matches = []
    needle = text.lower()
    for path in sorted(self._notes_root.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        if needle in content.lower():
            matches.append(path)
    ...
```
This soft-error pattern (exit 0, error text in `.text`) is exactly what ADR-0001 replaces with a raised `NotesRootError`.

> The skipped-note count is appended as a plain-text note at the end of the answer text.
>
> — `sad.md §8, Result surfacing row, verbatim` · full text: [sad.md](../sad.md)

**Flow 1 (happy path), flow 2 (bad root), flow 3 (no match / blank query), flow 4 (skip accounting):**
```
MD->>Notes: scan *.md files fresh
Notes-->>MD: file contents
MD->>MD: parse frontmatter, skip unreadable/malformed/escaping-symlink notes
MD->>MD: match significant words, rank, bound excerpt
MD-->>Core: Answer(text, sources)
```
```
MD->>MD: notes root missing or unreadable
MD--xCore: raises NotesRootError
```
```
alt query is blank or whitespace-only
    MD--xCore: raises BlankQueryError
else query has significant words
    MD->>MD: zero notes satisfy every significant word
    MD-->>Core: Answer(text="no matching notes", sources=[])
end
```
— `sad.md §6, flows 1–4, abridged` · full text: [sad.md](../sad.md)

**Fallback:** insufficient or contradicted by the code → read [sad.md](../sad.md) §5, §6 (all five flows), §8 and [adr/0001-dedicated-kberror-for-bad-notes-root.md](../adr/0001-dedicated-kberror-for-bad-notes-root.md) in full and follow them. Do not guess.

## Data delta

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `text` | `str` | — | ranked, excerpted matches; skipped-note count appended as plain text (sad.md §8 "Result surfacing") |
| `sources` | `list[str]` | — | matching notes' paths, in rank order |

— `data-model.md §In-process data shapes, table Answer, verbatim` · full text: [data-model.md](../data-model.md)

## API contract

- `kb query TEXT --mode markdown` observable behavior (`contracts/cli.md` §Behavior matrix): match found → stdout = ranked excerpts (+ trailing skipped-count line if any skips), exit 0; no match → "no matching notes" message, exit 0; blank text → stderr message, exit 1 (`BlankQueryError`); bad notes root → stderr message, exit 1 (`NotesRootError`).
- Error types: `NotesRootError(KbError)` raised when the configured notes root does not exist or cannot be read; `BlankQueryError(KbError)` raised when `TEXT` is blank/whitespace-only. Per-note failures (AC-06/07/08) are never raised.

— `contracts/cli.md §Behavior matrix, §Error codes, abridged` · full text: [contracts/cli.md](../contracts/cli.md)

## Acceptance criteria

### AC-04 — happy path

> **Given** no note under the notes root contains every significant word of the query
> **When** the Owner runs that query
> **Then** the system returns an explicit "no matching notes" answer rather than an error or an empty crash
>
> — `spec.md §5, AC-04, verbatim` · full text: [spec.md](../spec.md)

### AC-07 — domain invariant

> **Given** one note under the notes root is unreadable as a file, or has a missing or malformed Frontmatter block (as defined in AC-06)
> **When** the Owner runs a query that would otherwise match other, healthy notes
> **Then** the system still returns those other matches — one broken note never prevents the whole query from answering
>
> — `spec.md §5, AC-07, verbatim` · full text: [spec.md](../spec.md)

### AC-09 — cross-context

> **Given** the Owner adds or edits a note directly on disk after the backend was last used
> **When** the Owner immediately runs a new query
> **Then** the system reflects that on-disk change in the new query's results, without the Owner needing to run any separate reindex step
>
> — `spec.md §5, AC-09, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] Replace the stub body of `MarkdownBackend.query` in `src/kb/backends/markdown/backend.py`: raise `NotesRootError` (from `kb.core.knowledge_base`) when `self._notes_root` doesn't exist or isn't readable
- [ ] Raise `BlankQueryError` when `text.strip()` is empty
- [ ] Enumerate candidate files: `self._notes_root.rglob("*.md")`, excluding any path with a dot-prefixed segment (AC-10), fresh on every call (no caching — AC-09)
- [ ] Call `parse_note` (T3) per candidate; partition into healthy notes and skipped (`skip_reason is not None`) notes; keep a running skipped count
- [ ] Call T4's `significant_words`, `rank`, `bounded_excerpt` over the healthy notes only
- [ ] Build `Answer.text`: joined bounded excerpts (or "no matching notes" when the ranked list is empty), with a trailing plain-text skipped-count line appended only when `skipped > 0`
- [ ] Build `Answer.sources`: matching notes' paths, same order as the excerpts

## Edge cases

| Case | Behaviour |
|---|---|
| Notes root exists but is empty (no `.md` files) | Returns "no matching notes" `Answer`, not an error (AC-04) |
| Notes root does not exist | Raises `NotesRootError`, exit 1 (AC-04b, delivered by T2+T6) |
| Query is `"   "` (whitespace only) | Raises `BlankQueryError`, exit 1 (AC-05, delivered by T2) |
| One malformed note among otherwise-matching healthy notes | Healthy notes still returned; skipped count reflects the malformed one (AC-06, AC-07) |
| Note edited on disk between two queries | Second query reflects the edit — no cache, no stale state (AC-09) |

## Definition of Done

- [ ] Integration test (T7/T8, run after this task) exercises all five `sad.md` §6 flows end-to-end against `MarkdownBackend.query`
- [ ] `NotesRootError` and `BlankQueryError` propagate uncaught out of `query()` — the CLI's existing `except KbError` block (unchanged) handles them
- [ ] Every Hard Rule inlined above still holds (no caching, per-note isolation, skip accounting)
- [ ] lint + vet clean
