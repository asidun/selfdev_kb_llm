---
id: T7
title: "Integration tests: match, rank, excerpt, no-match, blank-query, fresh-scan"
layer: "tests"
deps: ["T5"]
blocks: []
acs: ["AC-01", "AC-02", "AC-02b", "AC-03", "AC-03b", "AC-04", "AC-05", "AC-09"]
files_hint: ["tests/backends/test_markdown_backend.py"]
owner: "Andrii Sidun"
estimate: "M"
context_budget: "M"
status: "todo"
step: ""
---

# T7 — Integration tests: match, rank, excerpt, no-match, blank-query, fresh-scan

## Place in the sequence

- **Blocked by:** T5 — Wire MarkdownBackend.query() pipeline · **Blocks:** none · **Wave:** 4 (parallel with T6, T9; shares a lane with T8).
- **Lane:** shares `tests/backends/test_markdown_backend.py` with T8 — serialized (both append to the same new test file; agree on file layout before either starts, or land them as sequential commits).

## Why (user story)

> **As an** Owner
> **I want** to query my notes with a multi-word question
> **So that** I get back relevant notes without needing to guess the exact phrase I used when writing them
>
> — `spec.md §4, US-01, verbatim` · full text: [spec.md](../spec.md)

This task is the real proof that T3+T4+T5 together deliver US-01/02/03/04/08 — it exercises `MarkdownBackend.query` end-to-end against a real temp-dir notes fixture, never mocking the filesystem.

## Inlined context

> Tests: pytest; integration tests for this backend use a real temp-dir notes fixture (frontmatter + malformed notes + symlinks), mirroring the existing "never mock the vector DB" convention applied to the filesystem instead of Chroma
>
> — `sad.md §2, Conventions, verbatim` · full text: [sad.md](../sad.md)

> - `tmp_path`-built notes root with a healthy note — `title`/`summary`/`tags` frontmatter + body — for the happy-path match/rank/excerpt assertions (AC-01, AC-02, AC-03).
> - A second healthy note whose frontmatter alone satisfies every significant word, to assert the Frontmatter-complete vs. body-completed rank split (AC-02) and the path-order tiebreak (AC-02b).
> - A blank/whitespace-only query string, to assert `BlankQueryError` (AC-05).
>
> — `data-model.md §Test fixtures, abridged` · full text: [data-model.md](../data-model.md)

**Fallback:** insufficient or contradicted by the code → read [data-model.md](../data-model.md) §Test fixtures and [sad.md](../sad.md) §6 flows 1 and 3 in full and follow them. Do not guess.

## Data delta

No DB changes — tests build `tmp_path` fixtures only, nothing persisted.

## API contract

Internal — tests call `MarkdownBackend.query(text)` directly (not through the CLI); CLI-level assertions belong to T6's `test_smoke.py` scope. See `contracts/cli.md` §Examples for the expected `Answer.text` shape this task's assertions should match.

## Acceptance criteria

### AC-01 — happy path

> **Given** the Owner's notes root contains a note whose Frontmatter (title, summary, tags) or body together contain every significant word of a question, where a word counts as present if it appears as a case-insensitive substring anywhere in that text (not necessarily as its own whole word)
> **When** the Owner queries the markdown backend with that multi-word question
> **Then** the system returns that note as a match, even though the exact phrase never appears verbatim in the note
>
> — `spec.md §5, AC-01, verbatim` · full text: [spec.md](../spec.md)

### AC-02 / AC-02b — happy path

> **Given** two notes each contain every significant word of the query somewhere across their Frontmatter and body, and one of them contains every significant word within its Frontmatter (title/summary/tags) alone, while the other only completes the match by also counting words found in its body
> **When** the Owner runs that query
> **Then** the system returns the note whose Frontmatter alone satisfied every significant word ahead of the note that needed its body to complete the match
>
> **Given** two or more notes tie for the same rank
> **When** the Owner runs that query
> **Then** the system always orders the tied notes the same way, by note path
>
> — `spec.md §5, AC-02 and AC-02b, verbatim` · full text: [spec.md](../spec.md)

### AC-03 / AC-03b — happy path

> **Given** a note matches the query inside a long passage of text
> **When** the Owner runs that query
> **Then** the system returns a bounded Excerpt around the match — respecting paragraph and block boundaries
>
> **Given** a query matches more notes than fit in one bounded answer
> **When** the Owner runs that query
> **Then** the system returns at most a fixed, bounded number of the top-ranked matching notes
>
> — `spec.md §5, AC-03 and AC-03b, verbatim` · full text: [spec.md](../spec.md)

### AC-04 — happy path

> **Given** no note under the notes root contains every significant word of the query
> **When** the Owner runs that query
> **Then** the system returns an explicit "no matching notes" answer rather than an error or an empty crash
>
> — `spec.md §5, AC-04, verbatim` · full text: [spec.md](../spec.md)

### AC-05 — error

> **Given** the Owner has not supplied any search terms (a blank or whitespace-only query)
> **When** the Owner runs that query
> **Then** the system explains that search terms are required instead of treating it as a match against every note
>
> — `spec.md §5, AC-05, verbatim` · full text: [spec.md](../spec.md)

### AC-09 — cross-context

> **Given** the Owner adds or edits a note directly on disk after the backend was last used
> **When** the Owner immediately runs a new query
> **Then** the system reflects that on-disk change in the new query's results, without the Owner needing to run any separate reindex step
>
> — `spec.md §5, AC-09, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] Create `tests/backends/test_markdown_backend.py` (mirrors `tests/backends/test_vector_backend.py` layout)
- [ ] `test_matches_scattered_significant_words` — AC-01: note's words spread across Frontmatter + body, query matches without exact phrase
- [ ] `test_frontmatter_complete_ranks_above_body_completed` — AC-02: two notes, assert rank order
- [ ] `test_tied_notes_ordered_by_path` — AC-02b: two same-bucket notes, assert deterministic path order across repeated calls
- [ ] `test_excerpt_is_bounded_and_block_aware` — AC-03: long note, assert excerpt length and that a code fence/table row isn't split
- [ ] `test_result_count_capped_at_ten` — AC-03b: >10 matching notes, assert only top 10 returned
- [ ] `test_no_match_returns_explicit_answer` — AC-04: query with no matching notes, assert `Answer.text` says so, no exception
- [ ] `test_blank_query_raises` — AC-05: `query("   ")` raises `BlankQueryError`
- [ ] `test_edit_between_queries_reflected` — AC-09: run query, edit a note file, run query again, assert the second result reflects the edit

## Edge cases

| Case | Behaviour |
|---|---|
| Query has zero significant words after stopword filtering (e.g. "the a of") | Treated as AC-04 "no matching notes" (not AC-05 — text wasn't blank), per `sad.md` §8 Matching row |
| Exactly 10 matching notes (boundary) | All 10 returned, none dropped (AC-03b "at most") |

## Definition of Done

- [ ] All checklist tests pass against the T5 implementation
- [ ] No mocking of the filesystem — real `tmp_path` fixtures only (repo convention)
- [ ] lint + vet clean
