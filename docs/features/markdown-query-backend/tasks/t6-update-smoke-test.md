---
id: T6
title: "Update test_smoke.py for the new NotesRootError exit-1 behavior"
layer: "tests"
deps: ["T5"]
blocks: []
acs: ["AC-04b"]
files_hint: ["tests/test_smoke.py"]
owner: "Andrii Sidun"
estimate: "S"
context_budget: "S"
status: "todo"
step: ""
---

# T6 — Update test_smoke.py for the new NotesRootError exit-1 behavior

## Place in the sequence

- **Blocked by:** T5 — Wire MarkdownBackend.query() pipeline · **Blocks:** none · **Wave:** 4 (parallel with T7, T8, T9).
- **Lane:** own lane — only file touched is `tests/test_smoke.py`.

## Why (user story)

> **As an** Owner
> **I want** the configured notes root does not exist or cannot be read to report a distinct configuration error
> **So that** a broken notes-root path is never indistinguishable from a topic the Owner genuinely has no notes on
>
> — `spec.md §4, US-04 context + AC-04b, abridged` · full text: [spec.md](../spec.md)

This task fixes the one existing test that asserts the superseded exit-0 soft-error behavior, so the suite reflects ADR-0001's raised-error convention instead of regressing it.

## Inlined context

> `tests/test_smoke.py` currently asserts the *old* soft-error behavior (exit 0, message in stdout) for a missing notes root
>
> — `sad.md §11, Risks and technical debt table, verbatim` · full text: [sad.md](../sad.md)

> `tests/test_smoke.py`'s `test_query_markdown_mode_on_missing_notes_root` must be updated in the same PR, since it currently asserts the superseded `exit_code == 0` behavior.
>
> — `data-model.md §Test fixtures, verbatim` · full text: [data-model.md](../data-model.md)

Current test (verified in repo, `tests/test_smoke.py`) to be updated:
```python
def test_query_markdown_mode_on_missing_notes_root(tmp_path, monkeypatch):
    monkeypatch.setenv("KB_NOTES_ROOT", str(tmp_path / "does-not-exist"))
    result = runner.invoke(app, ["query", "anything"])
    assert result.exit_code == 0
    assert "does not exist" in result.stdout
```

**Fallback:** insufficient or contradicted by the code → read [sad.md](../sad.md) §11 and [adr/0001-dedicated-kberror-for-bad-notes-root.md](../adr/0001-dedicated-kberror-for-bad-notes-root.md) in full and follow them. Do not guess.

## Data delta

No DB changes.

## API contract

`kb query TEXT --mode markdown` on a bad notes root: stderr one-line message, exit code 1 (`NotesRootError`) — `contracts/cli.md §Behavior matrix, row "Configured notes root missing or unreadable", verbatim` · full text: [contracts/cli.md](../contracts/cli.md)

## Acceptance criteria

### AC-04b — error

> **Given** the configured notes root does not exist or cannot be read
> **When** the Owner runs any query
> **Then** the system reports a distinct configuration error instead of the "no matching notes" answer, so a broken notes-root path is never indistinguishable from a topic the Owner genuinely has no notes on
>
> — `spec.md §5, AC-04b, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] In `tests/test_smoke.py`, change `test_query_markdown_mode_on_missing_notes_root` to assert `result.exit_code == 1`
- [ ] Assert the error message appears on `result.stderr` (via `CliRunner(mix_stderr=False)` or `result.output` depending on Typer's test runner configuration) instead of `result.stdout`
- [ ] Keep `test_cli_help_boots` unchanged — it is unaffected by this feature

## Edge cases

| Case | Behaviour |
|---|---|
| Notes root path exists but is a file, not a directory | Same `NotesRootError` path — "cannot be read" per AC-04b's wording covers this |

## Definition of Done

- [ ] `pytest tests/test_smoke.py` passes against the T5 implementation
- [ ] The updated assertion matches `contracts/cli.md`'s exit-code-1 contract, not the old exit-0 behavior
- [ ] lint + vet clean
