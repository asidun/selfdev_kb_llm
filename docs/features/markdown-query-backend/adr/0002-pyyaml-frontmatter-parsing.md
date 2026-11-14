---
status: Accepted
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "S"
ticket: "N/A"
---

# 0002 — Use PyYAML with a hand-rolled delimiter split for Frontmatter parsing

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Andrii Sidun (Architect), during `sdd:design`

## Context

The markdown backend must parse the required Frontmatter block (title, summary, tags) at the top of every note, and treat a missing or unparsable block as a skip (AC-06). `pyproject.toml` declares no YAML or frontmatter-parsing library at all today — `dependencies = ["typer>=0.12"]`, with `chromadb` only under the optional `vector` extra. Since markdown is the default query mode (`Settings.default_mode = "markdown"`) and must work without the vector extras installed, this backend needs its own, always-installed way to parse Frontmatter.

## Decision drivers

- `CLAUDE.md`'s convention of minimal, in-process dependencies — no DI framework, no unnecessary heavy libraries.
- Markdown mode must work standalone (`pip install -e .`, without `[vector]`), so the dependency has to live in the **base** `dependencies`, not an optional extra — unlike `chromadb`.
- AC-06 requires "missing or cannot be parsed" to be reliably detectable (broken YAML, missing keys) — the parser must distinguish a structural parse failure from a merely-empty block.

## Considered options

1. **`PyYAML` + a small hand-rolled `---`-delimiter split** — read the file, split on the leading `---\n...\n---` fence ourselves, hand the YAML body to `yaml.safe_load`. Minimal, well-understood, no project-specific markup conventions beyond what's already assumed.
2. **`python-frontmatter`** — a purpose-built library that does the delimiter split and YAML parsing in one call, plus some extras (TOML/JSON frontmatter support) this project doesn't need.
3. **A fully hand-rolled parser (no YAML library at all)** — parse `title:`/`summary:`/`tags:` lines with simple string splitting, no real YAML.

## Decision outcome

**Chosen:** Option 1. `PyYAML` is a minimal, ubiquitous, single-purpose dependency that does exactly the parsing AC-06 needs (and nothing else); the delimiter split itself is a few lines, not worth a whole extra library for. Option 2 pulls in frontmatter formats (TOML/JSON) this project never uses. Option 3 risks silently accepting malformed Frontmatter that real YAML parsing would correctly flag as unparsable — directly undermining AC-06's skip-detection requirement.

## Consequences

**Positive**
- Reliable, standards-based YAML parsing catches genuinely malformed Frontmatter (AC-06) that a hand-rolled line-splitter might silently misparse.
- Small, single-purpose dependency confined to `note.py` (§5) — no coupling to the rest of the codebase.
- Works in the base install, consistent with markdown being the default mode.

**Negative**
- One new mandatory dependency where there was none before — a (small) increase to every install's dependency footprint.

**Neutral**
- Swapping to `python-frontmatter` later, if its extra features become useful, is a localized change confined to `note.py`.

## Links

- Spec: [[../spec.md]] AC-06
- SAD: [[../sad.md]] §2, §4 (seed 5), §11
- Related ADR: [[0001-dedicated-kberror-for-bad-notes-root]]
