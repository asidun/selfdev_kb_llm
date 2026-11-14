---
id: T4
title: "Implement significant-word matching, Frontmatter-boosted ranking, and bounded excerpting"
layer: "domain"
deps: []
blocks: ["T5"]
acs: ["AC-01", "AC-02", "AC-02b", "AC-03", "AC-03b"]
files_hint: ["src/kb/backends/markdown/excerpt.py"]
owner: "Andrii Sidun"
estimate: "M"
context_budget: "M"
status: "todo"
step: ""
---

# T4 — Implement significant-word matching, Frontmatter-boosted ranking, and bounded excerpting

## Place in the sequence

- **Blocked by:** none · **Blocks:** T5 — Wire MarkdownBackend.query() pipeline · **Wave:** 1 (starts immediately, parallel with T1 and T2).
- **Lane:** own lane — only file touched is `src/kb/backends/markdown/excerpt.py` (new file); pure text-in/text-out, no filesystem access, unit-testable in isolation.

## Why (user story)

> **As an** Owner
> **I want** each matching note to come back as a short excerpt around the match
> **So that** the answer stays small enough for the LLM client consuming it, instead of dumping entire files
>
> — `spec.md §4, US-02, verbatim` · full text: [spec.md](../spec.md)

This task implements the pure matching/ranking/excerpting logic that `backend.py` (T5) will call per `Note` — the part of the pipeline with zero filesystem concerns.

## Inlined context

> `excerpt.py` <significant-word tokenizer + stopword filter, word-presence match, two-bucket Frontmatter-boosted rank with path-order tiebreak, block-aware bounded excerpt>
>
> — `sad.md §5, Internal decomposition, verbatim` · full text: [sad.md](../sad.md)

> A significant word = a query token after lowercasing and filtering a small common-English stopword list; "present" = case-insensitive substring anywhere in Frontmatter (title/summary/tags) or body (AC-01).
>
> — `sad.md §8, Matching row, verbatim` · full text: [sad.md](../sad.md)

> Two rank buckets, single-tier match rule: a note whose Frontmatter alone satisfies every significant word ranks above one that needed its body too; ties broken by ascending note path (AC-02, AC-02b).
>
> — `sad.md §8, Ranking row, verbatim` · full text: [sad.md](../sad.md)

> Bounded to ~5 lines of block-aware context (a fenced code block or table row is never split) around the passage with the most significant-word hits, first-occurrence tiebreak; at most the top 10 ranked notes per answer.
>
> — `sad.md §8, Excerpting row, verbatim` · full text: [sad.md](../sad.md)

**Fallback:** insufficient or contradicted by the code → read [sad.md](../sad.md) §8 and [spec.md](../spec.md) §8 Open questions in full and follow them. Do not guess.

## Data delta

No DB changes.

## API contract

Internal — no API surface.

## Acceptance criteria

### AC-01 — happy path

> **Given** the Owner's notes root contains a note whose Frontmatter (title, summary, tags) or body together contain every significant word of a question, where a word counts as present if it appears as a case-insensitive substring anywhere in that text (not necessarily as its own whole word)
> **When** the Owner queries the markdown backend with that multi-word question
> **Then** the system returns that note as a match, even though the exact phrase never appears verbatim in the note
>
> — `spec.md §5, AC-01, verbatim` · full text: [spec.md](../spec.md)

### AC-02 — happy path

> **Given** two notes each contain every significant word of the query somewhere across their Frontmatter and body, and one of them contains every significant word within its Frontmatter (title/summary/tags) alone, while the other only completes the match by also counting words found in its body
> **When** the Owner runs that query
> **Then** the system returns the note whose Frontmatter alone satisfied every significant word ahead of the note that needed its body to complete the match
>
> — `spec.md §5, AC-02, verbatim` · full text: [spec.md](../spec.md)

### AC-02b — happy path

> **Given** two or more notes tie for the same rank (for example, two Frontmatter hits, or two body-only hits)
> **When** the Owner runs that query
> **Then** the system always orders the tied notes the same way, by note path, so repeated queries return results in a stable order
>
> — `spec.md §5, AC-02b, verbatim` · full text: [spec.md](../spec.md)

### AC-03 — happy path

> **Given** a note matches the query inside a long passage of text
> **When** the Owner runs that query
> **Then** the system returns a bounded Excerpt around the match — respecting paragraph and block boundaries so a table row or code block is never cut in half — instead of the note's full content
>
> — `spec.md §5, AC-03, verbatim` · full text: [spec.md](../spec.md)

### AC-03b — happy path

> **Given** a query matches more notes than fit in one bounded answer
> **When** the Owner runs that query
> **Then** the system returns at most a fixed, bounded number of the top-ranked matching notes (exact number decided at design time, §8) instead of every match, so the answer size stays predictable for the calling LLM
>
> — `spec.md §5, AC-03b, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] `tokenize(text: str) -> list[str]`: lowercase, split on whitespace/punctuation, drop a small common-English stopword list
- [ ] `significant_words(query: str) -> list[str]`: tokenize the query text
- [ ] `frontmatter_text(frontmatter: dict) -> str` / `is_present(word, text) -> bool`: case-insensitive substring check
- [ ] `rank_bucket(note, significant_words) -> int | None`: `0` if Frontmatter alone satisfies every word, `1` if body needed, `None` if no match
- [ ] `rank(notes, significant_words) -> list[Note]`: sort by `(bucket, path)` ascending, drop non-matches, truncate to top 10 (AC-03b)
- [ ] `bounded_excerpt(note, significant_words) -> str`: find the ~5-line block-aware window around the passage with the most hits (first-occurrence tiebreak), never splitting a fenced code block (```` ``` ````-delimited) or a table row (`|`-delimited line)

## Edge cases

| Case | Behaviour |
|---|---|
| Query word present only as a substring of a longer word (e.g. query "cert", note has "certificate") | Counts as present — AC-01 explicitly allows substring match, "not necessarily as its own whole word" |
| Match passage sits at the very start/end of the note body | Excerpt window clamps to the note's actual boundaries, never pads with empty lines |
| Match passage falls inside a fenced code block | Excerpt widens to include the whole fenced block rather than cutting it (AC-03) |
| Match passage falls inside a markdown table row | Excerpt widens to include the whole row rather than cutting it (AC-03) |
| More than 10 notes match | Only the top 10 by `(bucket, path)` are returned (AC-03b) |
| Exactly two notes tie in the same bucket | Ordered by ascending `path` string, deterministically on every run (AC-02b) |

## Definition of Done

- [ ] Unit tests cover: stopword filtering, substring presence, Frontmatter-bucket vs. body-bucket ranking, path tiebreak, code-fence-safe excerpt, table-row-safe excerpt, top-10 truncation
- [ ] No filesystem access anywhere in this module (verified by the tests not using `tmp_path`/`Path.read_text`)
- [ ] lint + vet clean
