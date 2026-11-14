---
status: Draft
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "S"
---

# Spec — markdown-query-backend

> **Glossary:** [CONTEXT](./CONTEXT.md), [repo-root CONTEXT](../../../CONTEXT.md)
> **Reference module / docs / channels used:** None beyond the interview + repo docs already read (`CLAUDE.md`, `docs/architecture-map.md`, `docs/idea-brief.md`, `docs/adr/0001-0003`, the existing scaffold stub at `src/kb/backends/markdown/backend.py`).

## 1. Context

The Owner keeps a personal markdown notes folder and wants to query it from the CLI — typically by having an LLM client pass a natural-language question — and get a usable answer back without maintaining any embeddings or vector database (idea-brief §2, §7). Today's scaffold stub only does a literal case-insensitive substring scan and dumps whole matching files, which fails the Owner's actual usage pattern: multi-word questions rarely appear as an exact phrase, and dumping entire notes wastes the calling LLM's context window.

This is roadmap step 2 — the markdown-read half of the two-backend design settled in ADR 0002/0003 needs a real implementation before step 3 (vector/RAG) and step 4 (unified CLI mode switch) can build on it; the scaffold (step 1) left this backend as a placeholder.

Committed approach: the markdown Backend matches a query by requiring every significant word of the query to appear somewhere in a note (title/summary/tags/body), ranks a Frontmatter title/summary/tags hit above a body-only hit (tied equally among themselves, with path order as the final tiebreak), and returns a focused Excerpt per matching Note (bounded to a paragraph/block, never a severed table row or code fence) instead of the whole file — scoped to notes collections up to a few hundred files, matching the idea-brief's own threshold for when vector search becomes worth it instead. This feature also extends the shared `Answer` result (used by both backends behind the `Backend` protocol, ADR 0002) with a skipped-note count; the vector backend (roadmap step 3) decides independently whether and how to populate that same field — not scoped here.

Traceability / decision overrides from the devil's-advocate failure-mode pass run during this interview:
- Decision override: query matching changed from exact substring to all-significant-words-present — rationale: a literal substring scan returns nothing for most real multi-word questions, which would make the Owner stop using this mode entirely (invalidating the project's core per-query-switch premise).
- Decision override: Frontmatter changed from required to optional (with a visible skipped-note count in every Answer) — rationale: requiring Frontmatter made notes silently vanish from results and let the markdown and vector backends disagree on what's "in" the knowledge base; the original interview answer is superseded by this finding.
- Decision override: ranking tiebreak changed from "most recently modified" to note-path order — rationale: mtime ties become meaningless once the notes folder is git-cloned or checked out on a second machine (ADR 0003's own git-diffable workflow), making result order irreproducible across machines.

Size note: `docs/roadmap.md`'s step 2 entry carries an informal pre-classification estimate of "M", made before this feature was scoped. The `classify-size` walk run at the start of this interview (1 PR, ~1 week, one new internal API shape, internal-only breaking change — all owner-confirmed) produced **S**; `.size` is the source of truth going forward and `docs/roadmap.md` should be updated to match on the next roadmap pass.

## 2. Goals

- A query answers correctly for natural-language, multi-word questions, not just single keywords.
- A match returns a focused excerpt, not a whole-file dump, so answers stay small enough for an LLM caller's context.
- Every query returns a result deterministically and safely — a single malformed note or an unreadable file under the notes root never breaks the whole query, and a non-note file under the notes root is simply never considered (not counted as skipped, since it was never a note).

## 3. Non-goals

- Semantic / fuzzy / typo-tolerant matching — this backend is word-presence matching over plain text, not embeddings; that capability belongs to the vector backend (roadmap step 3).
- Automatic reindexing or caching of notes between queries — every query re-scans the notes root fresh; there is no index to go stale (markdown-as-source-of-truth, ADR 0003).
- Enforcing or validating the Owner's note-taking structure (folders like `inbox/`, `projects/`, `reference/`) — this backend reads whatever `.md` files exist under the notes root; organizing them is the Owner's own discipline, not the backend's job.
- Ranking by true relevance scoring (e.g. term frequency, BM25) — ranking here is a simple title/tags-boost-then-path-order rule, not an information-retrieval scoring model; that level of sophistication is what the vector backend exists for.

## 4. User stories

### US-01: Ask a natural-language question

**As an** Owner
**I want** to query my notes with a multi-word question
**So that** I get back relevant notes without needing to guess the exact phrase I used when writing them

### US-02: Get a focused excerpt, not a whole file

**As an** Owner
**I want** each matching note to come back as a short excerpt around the match
**So that** the answer stays small enough for the LLM client consuming it, instead of dumping entire files

### US-03: See the most relevant note first

**As an** Owner
**I want** notes whose title or tags match the query to rank above notes that only match in the body
**So that** I can trust the top result instead of scanning every match

### US-04: Be told when no note matches

**As an** Owner
**I want** a clear "no matching notes" answer when nothing fits my query
**So that** I know the knowledge base genuinely has nothing on the topic, instead of getting a confusing error

### US-05: Trust the answer even when a note is malformed

**As an** Owner
**I want** one unreadable or malformed note to never break my whole query
**So that** a single editing mistake in one file doesn't make the entire knowledge base unusable

### US-06: Know when notes were skipped

**As an** Owner
**I want** to see how many notes were skipped because they couldn't be read or parsed
**So that** I can tell "the knowledge base has no answer" apart from "the knowledge base silently ignored a note that might have had the answer"

### US-07: Stay inside the notes root

**As an** Owner
**I want** the backend to never follow a link outside my configured notes root
**So that** a query can never leak content from elsewhere on my machine into an answer

### US-08: Query against the current state of my notes

**As an** Owner
**I want** every query to reflect the notes exactly as they are on disk right now
**So that** I never have to remember to run a separate reindex step before trusting an answer

## 5. Acceptance criteria

### AC-01 (US-01) — happy path

**Given** the Owner's notes root contains a note whose title, tags, or body together contain every significant word of a question
**When** the Owner queries the markdown backend with that multi-word question
**Then** the system returns that note as a match, even though the exact phrase never appears verbatim in the note

### AC-02 (US-03) — happy path

**Given** two notes both contain every significant word of the query, one as a Frontmatter title/summary/tag hit and the other only in its body
**When** the Owner runs that query
**Then** the system returns the title/summary/tag-matching note ahead of the body-only match

### AC-02b (US-03) — happy path

**Given** two or more notes tie for the same rank (for example, two Frontmatter hits, or two body-only hits)
**When** the Owner runs that query
**Then** the system always orders the tied notes the same way, by note path, so repeated queries return results in a stable order

### AC-03 (US-02) — happy path

**Given** a note matches the query inside a long passage of text
**When** the Owner runs that query
**Then** the system returns a bounded Excerpt around the match — respecting paragraph and block boundaries so a table row or code block is never cut in half — instead of the note's full content

### AC-04 (US-04) — happy path

**Given** no note under the notes root contains every significant word of the query
**When** the Owner runs that query
**Then** the system returns an explicit "no matching notes" answer rather than an error or an empty crash

### AC-05 (US-01) — error

**Given** the Owner has not supplied any search terms (a blank or whitespace-only query)
**When** the Owner runs that query
**Then** the system explains that search terms are required instead of treating it as a match against every note

### AC-06 (US-06) — domain invariant

**Given** the notes root contains a note the system cannot read or parse (for example, broken Frontmatter)
**When** the Owner runs any query
**Then** the system never silently drops that note from consideration — it always counts it as skipped and reports the skipped count in the answer, so a skipped note is never indistinguishable from "no matches"

### AC-07 (US-05) — domain invariant

**Given** one note under the notes root is unreadable or malformed
**When** the Owner runs a query that would otherwise match other, healthy notes
**Then** the system still returns those other matches — one broken note never prevents the whole query from answering

### AC-08 (US-07) — authorization

**Given** the notes root contains a symbolic link pointing outside the configured notes root
**When** the Owner runs a query
**Then** the system never follows that link, so content outside the configured notes root can never appear in an answer

### AC-09 (US-08) — cross-context

**Given** the Owner adds or edits a note directly on disk after the backend was last used
**When** the Owner immediately runs a new query
**Then** the system reflects that on-disk change in the new query's results, without the Owner needing to run any separate reindex step

### AC-10 (US-01) — domain invariant

**Given** the notes root contains a non-markdown file (for example, an image or a binary file)
**When** the Owner runs any query
**Then** the system never considers that file as a candidate match and never counts it toward the skipped-note total, because it was never a note to begin with

## 6. Non-functional requirements

| Aspect | Target | Measurement |
|---|---|---|
| Latency p95, single query over a notes root up to a few hundred notes | ≤ 500 ms | wall-clock timing test against a synthetic fixture of 300 notes |
| Latency p95, single query over a notes root up to ~50 notes | ≤ 100 ms | same fixture approach, smaller size |
| Throughput | N/A — single-user interactive CLI, never serves concurrent callers | N/A |
| Availability | N/A — local single-process CLI, no uptime SLO; a crash is a non-zero exit, not downtime | N/A |
| Correctness — no silent note loss | 0 notes ever excluded from an answer without being counted in the skipped total (AC-06) | assertion in the test suite against a fixture containing ≥1 malformed note |

## 6.1 Security / privacy

- **Data classification:** Internal — the notes root may contain the Owner's private notes, but nothing in this feature exposes them beyond the Owner's own local machine.
- **Personal data touched:** None added by this feature — the backend only reads content the Owner already wrote; it introduces no new stored fields.
- **AuthZ/AuthN impact:** None — single local user, no accounts or roles. The one access-boundary control this feature adds is directory scope: the backend never reads content outside the configured notes root (AC-08).
- **Abuse cases:**
  - Symlink/path escape reading files outside the notes root: denied — symlinks pointing outside the notes root are never followed (AC-08).
  - A malformed or adversarially-crafted note crashing the whole query (denial of service against the Owner's own tool): denied — per-note isolation means one broken note never prevents other matches from being returned (AC-07).
  - An oversized note flooding the calling LLM's context through an unbounded match: denied — excerpts stay bounded to a paragraph/block regardless of note size (AC-03).
- **Security review:** N/A — single-user local CLI tool, no network exposure, no multi-tenant boundary, no new authorization surface.

## 7. Metrics / KPIs

- **Natural-language question match rate** — baseline: unmeasured, but by inspection today's literal-substring stub only succeeds when the question text appears verbatim in a note, so it fails most real multi-word questions, target: Owner-perceived useful answers for ≥80% of real questions asked, reviewed after 30 days of day-to-day markdown-mode use.
- **Whole-file dumps eliminated** — baseline: 100% of today's answers are full-file dumps, target: 0% of answers return a full file instead of a bounded excerpt, from this feature's first release.
- **Query failures caused by a malformed note** — baseline: unknown/undefined (today's stub has no per-note isolation), target: 0 queries fail due to a single malformed note, verified continuously via the malformed-note fixture in the test suite.

## 8. Open questions

- [ ] What's the exact bound on a "focused Excerpt" (line/character cap, how much context around the match)? Default now: a small fixed cap (roughly 3-5 lines of surrounding context), exact number decided at design time. — owner: Andrii Sidun, due: before `sdd:design`
- [ ] What counts as a "significant word" for query matching — does it filter common stopwords (a/the/is/of), or use every word the Owner typed? Default now: filter a small common-English stopword list. — owner: Andrii Sidun, due: before `sdd:design`
- [ ] How should the skipped-note count be surfaced in the answer — inline in the text, or a separate structured field? Default now: appended as a plain-text note in the answer. — owner: Andrii Sidun, due: before `sdd:api`
