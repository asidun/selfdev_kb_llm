---
status: Accepted
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "S"
ticket: "N/A"
---

# 0001 — Raise a dedicated KbError subclass for a missing or unreadable notes root

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Andrii Sidun (Architect), during `sdd:design`

## Context

AC-04b requires that a missing or unreadable notes root produce a "distinct configuration error," never indistinguishable from a genuine "no matching notes" answer. The current scaffold stub does not do this: `MarkdownBackend.query()` detects the missing root and returns a normal `Answer` with the error message baked into `.text` — the CLI prints it to stdout and exits 0, the same as any other successful query. Meanwhile, `CLAUDE.md`'s own documented convention is a single `KbError` hierarchy, caught once at the CLI's top, printed to stderr, exit non-zero — and the CLI (`src/kb/cli/main.py`) already implements exactly that catch block for `UnknownBackendError`. The markdown backend's missing-root case is the one place that convention isn't followed.

## Decision drivers

- AC-04b: a broken notes-root path must never be indistinguishable from "the Owner genuinely has no notes on this topic."
- `CLAUDE.md` "Errors": a single `KbError` hierarchy; the CLI catches at the top and prints one line + exits non-zero — an existing, already-implemented convention for `UnknownBackendError`.
- Spec §6.1: no new authorization surface, but directory-scope *is* the one access-boundary control this feature owns — a configuration failure around that boundary deserves to be loud, not folded into normal output.

## Considered options

1. **Raise a new `NotesRootError(KbError)` when the configured notes root doesn't exist or can't be read** — the CLI's existing top-level `except KbError` catch handles it for free: one stderr line, exit 1, no new CLI code needed.
2. **Keep the current pattern: return an `Answer` with the error message in `.text`** — zero CLI changes, but perpetuates the exit-0 behavior that makes a broken path indistinguishable from "no results" to any caller that checks the exit code (which is exactly what AC-04b asks to avoid), and leaves the one raised-vs-returned inconsistency in the codebase.

## Decision outcome

**Chosen:** Option 1. Raising `NotesRootError(KbError)` satisfies AC-04b precisely (a configuration error is structurally different from a successful `Answer`, not just different text inside one), costs no new CLI code since the top-level `except KbError` catch already exists for `UnknownBackendError`, and removes the one place the codebase doesn't follow its own documented error convention.

## Consequences

**Positive**
- AC-04b is satisfied structurally (differing exception type + exit code), not just by message wording.
- No new CLI code — reuses the existing `except KbError as exc: typer.echo(..., err=True); raise typer.Exit(code=1)` block verbatim.
- Removes a documented inconsistency between the markdown backend and the rest of the codebase's error handling.

**Negative**
- `tests/test_smoke.py` currently asserts the old behavior (exit 0, message in stdout) for a missing notes root and must be updated in the same change.
- Any caller that was relying on the old exit-0-with-message behavior (none known — the stub is pre-release) breaks; acceptable since this backend has not shipped a real implementation yet.

**Neutral**
- `NotesRootError`'s exact message text is an implementation detail decided during `tasks`/`implement`, not fixed here.

## Links

- Spec: [[../spec.md]] AC-04b
- SAD: [[../sad.md]] §4, §6 (flow 2), §8 (Error handling)
- Related ADR: N/A
