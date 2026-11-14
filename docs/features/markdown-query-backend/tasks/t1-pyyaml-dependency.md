---
id: T1
title: "Add PyYAML as a base (non-optional) dependency"
layer: "wiring"
deps: []
blocks: ["T3"]
acs: []
files_hint: ["pyproject.toml"]
owner: "Andrii Sidun"
estimate: "S"
context_budget: "S"
status: "todo"
step: ""
---

# T1 — Add PyYAML as a base (non-optional) dependency

## Place in the sequence

- **Blocked by:** none · **Blocks:** T3 — Implement Note parsing with Frontmatter + skip/symlink detection · **Wave:** 1 (starts immediately, parallel with T2 and T4).
- **Lane:** own lane — only file touched is `pyproject.toml`.

## Why (user story)

> **As an** Owner
> **I want** to query my notes with a multi-word question
> **So that** I get back relevant notes without needing to guess the exact phrase I used when writing them
>
> — `spec.md §4, US-01, verbatim` · full text: [spec.md](../spec.md)

This task adds the parsing dependency (PyYAML) that every downstream Frontmatter read needs, with no code of its own.

## Inlined context

> **Chosen:** Option 1. `PyYAML` is a minimal, ubiquitous, single-purpose dependency that does exactly the parsing AC-06 needs (and nothing else); the delimiter split itself is a few lines, not worth a whole extra library for. [...] Markdown mode must work standalone (`pip install -e .`, without `[vector]`), so the dependency has to live in the **base** `dependencies`, not an optional extra — unlike `chromadb`.
>
> — `adr/0002-pyyaml-frontmatter-parsing.md §Decision outcome / §Decision drivers, abridged` · full text: [adr/0002-pyyaml-frontmatter-parsing.md](../adr/0002-pyyaml-frontmatter-parsing.md)

Current state (verified in repo): `pyproject.toml` declares `dependencies = ["typer>=0.12"]` with `chromadb` only under the optional `[project.optional-dependencies].vector` extra — no YAML library anywhere today.

**Fallback:** insufficient or contradicted by the code → read [adr/0002-pyyaml-frontmatter-parsing.md](../adr/0002-pyyaml-frontmatter-parsing.md) in full and follow it. Do not guess.

## Data delta

No DB changes.

## API contract

Internal — no API surface.

## Acceptance criteria

No spec §5 AC maps directly to this task; it is the dependency prerequisite for AC-06 (T3) and AC-08 (T3), which require PyYAML parsing to exist before they can be implemented.

## Checklist

- [ ] Add `"PyYAML>=6.0"` to `[project].dependencies` in `pyproject.toml`
- [ ] Run `pip install -e ".[vector,dev]"` to confirm the base install resolves PyYAML without the `vector` extra
- [ ] Confirm `import yaml` succeeds in a bare `pip install -e .` (no extras) environment

## Edge cases

| Case | Behaviour |
|---|---|
| `vector` extra installed alongside base | No conflict — `PyYAML` and `chromadb` have no overlapping pin |
| Fresh install without any extras | `import yaml` still succeeds (base dependency, ADR-0002) |

## Definition of Done

- [ ] `pyproject.toml` lists `PyYAML` in `dependencies` (not `optional-dependencies`)
- [ ] `pip install -e .` (no extras) succeeds and `python -c "import yaml"` succeeds
- [ ] lint + vet clean
