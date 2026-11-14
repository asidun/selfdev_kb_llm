---
id: T9
title: "NFR performance test: p95 latency at 300-note and 50-note scale"
layer: "tests"
deps: ["T5"]
blocks: []
acs: []
files_hint: ["tests/backends/test_markdown_backend_perf.py"]
owner: "Andrii Sidun"
estimate: "S"
context_budget: "S"
status: "todo"
step: ""
---

# T9 — NFR performance test: p95 latency at 300-note and 50-note scale

## Place in the sequence

- **Blocked by:** T5 — Wire MarkdownBackend.query() pipeline · **Blocks:** none · **Wave:** 4 (parallel with T6, T7, T8).
- **Lane:** own lane — new file `tests/backends/test_markdown_backend_perf.py`, independent of T7/T8's shared file.

## Why (user story)

> **As an** Owner
> **I want** to query my notes with a multi-word question
> **So that** I get back relevant notes without needing to guess the exact phrase I used when writing them
>
> — `spec.md §4, US-01, verbatim` · full text: [spec.md](../spec.md)

A query that answers correctly but too slowly still fails the Owner's interactive CLI usage pattern — this task is the NFR gate that holds the single-pass synchronous scan (sad.md §4 seed 4) to its documented latency budget.

## Inlined context

> | Latency p95, single query over a notes root up to a few hundred notes | ≤ 500 ms | wall-clock timing test against a synthetic fixture of 300 notes, each with ~2–5 KB of body text (including at least one note long enough to exercise AC-03's bounded-excerpt path); p95 measured across 20 distinct representative queries, each run once |
> | Latency p95, single query over a notes root up to ~50 notes | ≤ 100 ms | same fixture approach (2–5 KB notes, 20 distinct queries run once each), smaller fixture size |
>
> — `spec.md §6, NFR table, verbatim` · full text: [spec.md](../spec.md)

> **When:** a single query runs over a notes root of up to a few hundred notes.
> **Then:** p95 latency ≤ 500 ms over a 300-note fixture [...]; p95 ≤ 100 ms over a ~50-note fixture, same methodology.
> **How verify:** wall-clock timing test against the synthetic fixtures described above.
>
> — `sad.md §10, QG-3, abridged` · full text: [sad.md](../sad.md)

> No new datastore, no caching, single-pass synchronous scan per query. [...] The NFR's latency budget (≤500 ms @ 300 notes) is met by a synchronous `Path.rglob` walk with no concurrency — consistent with the non-goals' own scale ceiling ("a few hundred files").
>
> — `sad.md §4, Solution strategy seed 4, abridged` · full text: [sad.md](../sad.md)

**Fallback:** insufficient or contradicted by the code → read [spec.md](../spec.md) §6 and [sad.md](../sad.md) §10 QG-3 in full and follow them. Do not guess.

## Data delta

No DB changes — synthetic fixture built under `tmp_path`, nothing persisted.

## API contract

Internal — no API surface; this is a non-functional timing test against `MarkdownBackend.query` called directly.

## Acceptance criteria

This task verifies spec §6's NFR table (quoted above under *Inlined context*), not a numbered §5 acceptance criterion — no `acs` entry applies. Its Definition of Done is the NFR's own measurement method, carried verbatim above.

## Checklist

- [ ] Create `tests/backends/test_markdown_backend_perf.py`
- [ ] Build a `tmp_path` fixture generator: N notes, each with valid Frontmatter (`title`, `summary`, `tags`) and ~2–5 KB of body text; include at least one note long enough to exercise the bounded-excerpt path (AC-03)
- [ ] `test_p95_latency_under_500ms_at_300_notes`: generate 300 notes, run 20 distinct representative queries once each, assert p95 wall-clock time ≤ 500 ms
- [ ] `test_p95_latency_under_100ms_at_50_notes`: generate 50 notes, same methodology, assert p95 ≤ 100 ms
- [ ] Mark both tests so they can be skipped/excluded from the fast default `pytest` run if they prove flaky on CI hardware (e.g. a `@pytest.mark.slow` marker), without removing them from the suite

## Edge cases

| Case | Behaviour |
|---|---|
| Test run on slower CI hardware than the Owner's local machine | Acceptable per sad.md §11 risk table — the numbers are design-time defaults, revisit after the 30-day KPI self-review if they prove unrealistic in CI |

## Definition of Done

- [ ] Both latency tests pass locally against the T5 implementation
- [ ] Fixture generation matches spec §6's exact methodology (2–5 KB/note, 20 distinct queries, p95 across them)
- [ ] lint + vet clean
