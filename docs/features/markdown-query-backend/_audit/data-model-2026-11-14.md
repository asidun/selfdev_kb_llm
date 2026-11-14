# Data-model audit — markdown-query-backend — 2026-11-14

## Outcome

**No schema change.** Zero migrations staged. `docs/features/markdown-query-backend/data-model.md`
documents the feature's in-process data shapes (`Note`, the existing `Answer`) instead, per the
skill's legitimate "no schema change" outcome.

## Convention derivation (step 2)

- `architecture-map.md` frontmatter: `migration_tool: ""` — "no relational DB; the vector
  backend's own store is the persistence."
- `sad.md` §2 Constraints: "No new datastore — markdown files on local disk remain the sole source
  of truth (ADR 0003); no relational DB, no migrations."
- `sad.md` §4 seed 4: "No new datastore, no caching, single-pass synchronous scan per query."
- `sad.md` §8 Persistence row: "Markdown files remain the sole source of truth; no index, no
  cache; every query re-scans fresh (AC-09)."
- Live repo: no `migrations/` directory exists anywhere in the tree (confirmed by search); no
  relational or vector schema is touched by this feature — the existing `ChromaStore` (vector
  backend) is untouched and out of scope here.

**Promote-time hint:** N/A — there is nothing for `implement` to promote. No migration ordinal was
reserved.

## Staged migrations

None. `docs/features/markdown-query-backend/migrations/` was deliberately not created.

## Convention deviations

None — the repo's own stated convention ("no relational DB, no migrations") is followed exactly;
this feature does not diverge from it.

## Drift detection (step 11)

No domain layer with persisted/DB-backed fields exists for this feature to drift against — the
`Note` and `Answer` shapes documented in `data-model.md` are in-process only, re-derived fresh on
every query (AC-09), never written to a store. No `field-without-column` / `column-without-field`
/ `type-mismatch` / `nullability-mismatch` findings apply. No `_drift/` directory was created.

## Self-check (step 12)

| Check | Result |
|---|---|
| Naming matches repo convention | N/A — no schema introduced |
| Down reversibility (every CREATE has a DROP, etc.) | N/A — no migrations |
| FK indexes (every FK has an index) | N/A — no FK, no datastore |
| Convention adherence | Pass — explicitly follows the repo's "no relational DB, no migrations" convention; no house style imposed |

## Open questions carried from upstream

- spec §8 OQ3 (skipped-count surfacing format: inline text vs. structured field) stays open until
  `sdd:api` — `sad.md` §1 already narrowed data-model's own `Answer` shape question (2-field, text
  surfacing for v1), so nothing is deferred to `api` on the *data* side beyond that wording choice.

## Next stage

`sdd:api markdown-query-backend` — per the skill's N/A condition ("no contract change: no new/
changed endpoint, event, or public signature"), this feature *does* change a public signature
(the `MarkdownBackend.query` behavior, `NotesRootError`/`BlankQueryError` additions to the `KbError`
hierarchy, and the pending OQ3 surfacing-format decision), so `api` should run rather than be
skipped.
