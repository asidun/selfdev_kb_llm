---
id: T2
title: "Add NotesRootError and BlankQueryError to the KbError hierarchy"
layer: "domain"
deps: []
blocks: ["T5"]
acs: ["AC-04b", "AC-05"]
files_hint: ["src/kb/core/knowledge_base.py"]
owner: "Andrii Sidun"
estimate: "S"
context_budget: "S"
status: "todo"
step: ""
---

# T2 — Add NotesRootError and BlankQueryError to the KbError hierarchy

## Place in the sequence

- **Blocked by:** none · **Blocks:** T5 — Wire MarkdownBackend.query() pipeline · **Wave:** 1 (starts immediately, parallel with T1 and T4).
- **Lane:** own lane — only file touched is `src/kb/core/knowledge_base.py`.

## Why (user story)

> **As an** Owner
> **I want** a clear "no matching notes" answer when nothing fits my query
> **So that** I know the knowledge base genuinely has nothing on the topic, instead of getting a confusing error
>
> — `spec.md §4, US-04, verbatim` · full text: [spec.md](../spec.md)

This task creates the two new error types that let a configuration failure (bad notes root) and a bad call (blank query) be raised as structurally distinct outcomes from "no matching notes."

## Inlined context

> **Chosen:** Option 1. Raising `NotesRootError(KbError)` satisfies AC-04b precisely (a configuration error is structurally different from a successful `Answer`, not just different text inside one), costs no new CLI code since the top-level `except KbError` catch already exists for `UnknownBackendError`.
>
> — `adr/0001-dedicated-kberror-for-bad-notes-root.md §Decision outcome, verbatim` · full text: [adr/0001-dedicated-kberror-for-bad-notes-root.md](../adr/0001-dedicated-kberror-for-bad-notes-root.md)

> This feature adds `NotesRootError(KbError)` for a missing/unreadable notes root (ADR-0001) and, by the same convention, a `BlankQueryError(KbError)` for a blank/whitespace-only query (AC-05) — both are caller/configuration-input errors, raised once per call.
>
> — `sad.md §8, Error handling row, verbatim` · full text: [sad.md](../sad.md)

Existing code (`src/kb/core/knowledge_base.py`, verified in repo) already has the pattern to follow:
```python
class KbError(Exception):
    """Base for every error raised across kb modules."""


class UnknownBackendError(KbError):
    pass
```
The CLI (`src/kb/cli/main.py`) already catches `KbError` at the top, prints to stderr, exits 1 — no CLI changes are needed once these subclasses exist.

**Fallback:** insufficient or contradicted by the code → read [adr/0001-dedicated-kberror-for-bad-notes-root.md](../adr/0001-dedicated-kberror-for-bad-notes-root.md) and [sad.md](../sad.md) §8 in full and follow them. Do not guess.

## Data delta

No DB changes.

## API contract

Internal — no API surface. (The CLI-observable behavior these errors produce is fixed in `contracts/cli.md` §Error codes: `NotesRootError` and `BlankQueryError`, both exit code 1 — see [contracts/cli.md](../contracts/cli.md).)

## Acceptance criteria

### AC-04b — error

> **Given** the configured notes root does not exist or cannot be read
> **When** the Owner runs any query
> **Then** the system reports a distinct configuration error instead of the "no matching notes" answer, so a broken notes-root path is never indistinguishable from a topic the Owner genuinely has no notes on
>
> — `spec.md §5, AC-04b, verbatim` · full text: [spec.md](../spec.md)

### AC-05 — error

> **Given** the Owner has not supplied any search terms (a blank or whitespace-only query)
> **When** the Owner runs that query
> **Then** the system explains that search terms are required instead of treating it as a match against every note
>
> — `spec.md §5, AC-05, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] Add `class NotesRootError(KbError): pass` to `src/kb/core/knowledge_base.py`
- [ ] Add `class BlankQueryError(KbError): pass` to `src/kb/core/knowledge_base.py`
- [ ] Keep both next to the existing `UnknownBackendError(KbError)` definition for discoverability

## Edge cases

| Case | Behaviour |
|---|---|
| Both errors raised in the same call (impossible in practice — root check happens before blank-text check, or vice versa) | Only one is ever raised per call; T5 decides the check order |
| A caller catches `KbError` generically | Both subclasses are still caught — no behavior change for existing `except KbError` blocks |

## Definition of Done

- [ ] `NotesRootError(KbError)` and `BlankQueryError(KbError)` exist in `src/kb/core/knowledge_base.py`
- [ ] Unit test (or doctest) confirms both are instances of `KbError`
- [ ] lint + vet clean
