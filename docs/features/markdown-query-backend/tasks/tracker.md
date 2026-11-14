# Tracker — markdown-query-backend

> Status of every task in the epic. `implement` updates **Status** and **Step** after every
> subagent it runs (and commits them with the task), so this table shows where the run is right now.
> Status: `todo` · `in_progress` · `blocked` · `review` · `done`.
> Step: `SELECT` · `RED` · `GREEN` · `REFACTOR` · `GATE` · `REVIEW` · `COMMIT` (`—` before the task starts).
> A `blocked` row carries its reason in Step, e.g. `GATE — lint red after 3 retries`.

| # | Task | Layer | Owner | Estimate | Blocked by | Status | Step |
|---|---|---|---|---|---|---|---|
| T1 | Add PyYAML as a base dependency | wiring | Andrii Sidun | S | — | todo | — |
| T2 | Add NotesRootError/BlankQueryError | domain | Andrii Sidun | S | — | todo | — |
| T3 | Implement Note parsing + skip/symlink detection | domain | Andrii Sidun | M | T1 | todo | — |
| T4 | Implement matching/ranking/excerpting | domain | Andrii Sidun | M | — | todo | — |
| T5 | Wire MarkdownBackend.query() pipeline | app | Andrii Sidun | M | T2, T3, T4 | todo | — |
| T6 | Update test_smoke.py | tests | Andrii Sidun | S | T5 | todo | — |
| T7 | Integration tests: match/rank/no-match/blank/fresh-scan | tests | Andrii Sidun | M | T5 | todo | — |
| T8 | Integration tests: skip/symlink/non-md | tests | Andrii Sidun | M | T5 | todo | — |
| T9 | NFR performance test | tests | Andrii Sidun | S | T5 | todo | — |

**Total:** 9 tasks, ~1 person-week (feature size S, per `.size`).
