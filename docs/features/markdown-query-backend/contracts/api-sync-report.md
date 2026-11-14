---
status: Draft
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "S"
---

# Contract sync report — markdown-query-backend

Interface kind: `cli` → `contracts/cli.md` (no `data-model.md` gate issue: the file exists and was
read; no schema change either way — the entities below are in-process shapes, not DB tables, per
`data-model.md`'s own "No relational/vector schema change" section).

## Section A — field/behavior-origins table

One row per observable CLI output element, tracing to its source artifact.

| cli.md element | origin | confidence |
|---|---|---|
| `query` command signature (`TEXT`, `--mode`) | existing code — `src/kb/cli/main.py` (unchanged by this feature) | high |
| Blank-`TEXT` rejection | `spec.md` AC-05 → `sad.md` §6 flow 3 (alt-branch), §8 "Error handling" row | high |
| `NotesRootError` / exit 1 on bad notes root | `spec.md` AC-04b → `sad.md` §6 flow 2, ADR-0001 | high |
| Ranked, excerpted match output | `data-model.md` `Answer.text` → `spec.md` AC-01/AC-02/AC-02b/AC-03 → `sad.md` §6 flow 1, §8 "Ranking"/"Excerpting" rows | high |
| Top-10 result cap | `sad.md` §8 "Excerpting" row (design-time default, spec §8 OQ1) | high |
| ~5-line block-aware excerpt bound | `sad.md` §8 "Excerpting" row (design-time default, spec §8 OQ1) | high |
| "no matching notes" message / exit 0 | `spec.md` AC-04 → `sad.md` §6 flow 3 (else-branch) | high |
| Trailing skipped-count line | `data-model.md` `Answer` shape note (count appended to `.text`, not a new field) → `spec.md` AC-06 → `sad.md` §6 flow 4, §8 "Result surfacing" row | high |
| Symlink-escape exclusion folded into skip accounting | `spec.md` AC-08 → `sad.md` §6 flow 5, §8 "Symlink handling" row | high |
| Non-`.md` / dot-path files invisible (not skipped, not matched) | `spec.md` AC-10 → `sad.md` §8 "Skip accounting" row | high |
| Exact stdout wording for each message | not fixed by any source — ADR-0001 "Neutral" consequence defers exact message text to `tasks`/`implement` | medium |
| `Answer.sources` ordering mirrors printed rank order | `data-model.md` `Answer` shape (unchanged 2-field dataclass) | high |

No `low`-confidence rows — every behavioral element in `cli.md` traces to a concrete AC, sequence
flow, or existing code; the single `medium` row (exact message wording) is an intentional
implementation-time decision, not a derivation gap.

## Section B — drift findings (4-point checklist, CLI form)

1. **Command/output ↔ data-model** *(core)* — ✓. The one command (`query`) reads `Note` entities
   (via `MarkdownBackend`) and produces output shaped by the unchanged `Answer(text, sources)`
   dataclass; no field in `cli.md` lacks a `data-model.md` origin.
2. **Error code ↔ repo error definition** *(core)* — ✓ with a note. `NotesRootError` and
   `BlankQueryError` do not yet exist in `src/kb/core/knowledge_base.py` (today: `KbError`,
   `UnknownBackendError` only) — this is **expected forward derivation**, not drift: ADR-0001
   explicitly specifies `NotesRootError` as new, and `BlankQueryError` follows the same documented
   `KbError` convention (`CLAUDE.md` "Errors") already used for `UnknownBackendError`. Both are
   specified here for `tasks`/`implement` to create; no existing error registry entry contradicts
   them.
3. **Validation/behavior ↔ constraint** *(core)* — ✓. The ~5-line excerpt bound, top-10 result
   cap, and stopword-filtered significant-word matching in `cli.md` match `sad.md` §8's
   "Excerpting"/"Matching" rows verbatim (both are design-time defaults from `spec.md` §8 OQ1/OQ2,
   now fixed by `sad.md`, carried through unchanged here).
4. **CLI output ↔ sequence** *(supporting)* — ✓. All 5 `sad.md` §6 flows have a corresponding
   behavior-matrix row in `cli.md`: flow 1 (happy path), flow 2 (bad notes root), flow 3
   (blank-query alt-branch / no-match else-branch), flow 4 (malformed-note skip), flow 5
   (symlink-escape skip).

**Back-feed (coverage cross-check):**

- Every `spec.md` §5 AC (AC-01 through AC-10, including AC-02b/AC-03b/AC-04b) maps to ≥1
  behavior-matrix row in `cli.md`, **except AC-09** ("query reflects current on-disk state") —
  this AC describes an absence of caching/staleness, not an observable output shape; it has no
  CLI-surface representation to contract and is correctly out of scope for this document (verified
  by test, per `sad.md` §10 QG-1/§11, not by the interface contract).
- Every `cli.md` row maps to a `spec.md` §4 user story (US-01 through US-08) and ≥1 AC — no
  orphan rows.
- Every `sad.md` §6 `alt`/`else` branch has a corresponding row: flow 2's error path →
  "Configured notes root missing" row; flow 3's alt (blank query) → "Blank/whitespace-only TEXT"
  row; flow 3's else (no match) → "No note matches" row; flow 4's alt (skip) → "matches with skips"
  row; flow 5's alt (reject symlink) → "Symlink escaping" row. No sequence gap found.

**Result: 0 core findings failing, 0 flags of any kind.** Proceeding to lint/commit (no `--fix`,
`--accept`, `--oq`, or `--drop` dialog needed).

## Reconcile note

Re-run `/sdd:api markdown-query-backend --reconcile` if `data-model.md`'s `Note`/`Answer` shapes
change, or if `sad.md` §6/§8 gain a new flow or crosscutting-concept row, before `tasks` starts.
