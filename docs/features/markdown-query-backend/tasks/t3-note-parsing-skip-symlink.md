---
id: T3
title: "Implement Note parsing with Frontmatter, skip accounting, and symlink-escape detection"
layer: "domain"
deps: ["T1"]
blocks: ["T5"]
acs: ["AC-06", "AC-08", "AC-10"]
files_hint: ["src/kb/backends/markdown/note.py"]
owner: "Andrii Sidun"
estimate: "M"
context_budget: "M"
status: "todo"
step: ""
---

# T3 — Implement Note parsing with Frontmatter, skip accounting, and symlink-escape detection

## Place in the sequence

- **Blocked by:** T1 — Add PyYAML as a base dependency · **Blocks:** T5 — Wire MarkdownBackend.query() pipeline · **Wave:** 2.
- **Lane:** own lane — only file touched is `src/kb/backends/markdown/note.py` (new file).

## Why (user story)

> **As an** Owner
> **I want** one unreadable or malformed note to never break my whole query
> **So that** a single editing mistake in one file doesn't make the entire knowledge base unusable
>
> — `spec.md §4, US-05, verbatim` · full text: [spec.md](../spec.md)

This task builds the per-note parsing step that detects (without raising) every reason a note must be excluded and counted as skipped: unreadable file, missing/malformed Frontmatter, or a symlink escaping the notes root.

## Inlined context

> `note.py` <Note dataclass (path, frontmatter dict, body); parse_note(path, notes_root) -> Note, raising/flagging a skip reason for unreadable files, missing/malformed Frontmatter, or a symlink that escapes the notes root / loops>
>
> — `sad.md §5, Internal decomposition, verbatim` · full text: [sad.md](../sad.md)

> A symlink is resolved via `Path.resolve()`; rejected and counted as skipped when the resolved target falls outside the notes root (`is_relative_to` check) or resolution raises (a loop); otherwise followed and searched normally.
>
> — `sad.md §8, Symlink handling row, verbatim` · full text: [sad.md](../sad.md)

> A note is skipped (excluded from matching, counted in the total) when it is unreadable as a file, or its Frontmatter block is missing/unparsable (AC-06). Never skipped and never counted when it is not a `.md` file, or sits under a dot-prefixed file/directory (AC-10).
>
> — `sad.md §8, Skip accounting row, verbatim` · full text: [sad.md](../sad.md)

> **Chosen:** Option 1. `PyYAML` + a small hand-rolled `---`-delimiter split — read the file, split on the leading `---\n...\n---` fence ourselves, hand the YAML body to `yaml.safe_load`.
>
> — `adr/0002-pyyaml-frontmatter-parsing.md §Considered options, Option 1, abridged` · full text: [adr/0002-pyyaml-frontmatter-parsing.md](../adr/0002-pyyaml-frontmatter-parsing.md)

**Fallback:** insufficient or contradicted by the code → read [sad.md](../sad.md) §5 and §8 and [adr/0002-pyyaml-frontmatter-parsing.md](../adr/0002-pyyaml-frontmatter-parsing.md) in full and follow them. Do not guess.

## Data delta

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `path` | `Path` | relative to notes root | identity for ranking tiebreak (AC-02b) and `sources` |
| `frontmatter` | `dict[str, Any]` \| `None` | `None` when missing/unparsable → note is skipped | parsed via PyYAML (ADR-0002); expected keys `title`, `summary`, `tags` |
| `body` | `str` | — | raw markdown body, post-frontmatter-delimiter |
| `skip_reason` | `str` \| `None` | `None` when healthy | set for unreadable file, missing/malformed frontmatter (AC-06), or an escaping/looping symlink (AC-08) |

— `data-model.md §In-process data shapes, table Note, verbatim` · full text: [data-model.md](../data-model.md)

## API contract

Internal — no API surface.

## Acceptance criteria

### AC-06 — domain invariant

> **Given** the notes root contains a note the system cannot read as a file (for example, a permissions error or invalid encoding), or whose Frontmatter block is missing or cannot be parsed (for example, broken YAML, or a missing title/summary/tags block)
> **When** the Owner runs any query
> **Then** the system never silently drops that note from consideration — it always counts it as skipped, excludes it entirely from matching, and reports the skipped count in the answer, so a skipped note is never indistinguishable from "no matches"
>
> — `spec.md §5, AC-06, verbatim` · full text: [spec.md](../spec.md)

### AC-08 — authorization

> **Given** the notes root contains a symbolic link whose resolved target lies outside the configured notes root, or a symbolic link that loops back on itself
> **When** the Owner runs a query
> **Then** the system never includes content from that link in an answer — it resolves the link, rejects it (counting it toward the skipped total, per AC-06) when the resolved target falls outside the notes root or forms a loop, while a symbolic link whose resolved target lies inside the configured notes root is followed and searched normally
>
> — `spec.md §5, AC-08, verbatim` · full text: [spec.md](../spec.md)

### AC-10 — domain invariant

> **Given** the notes root contains a file that is not a markdown file with a `.md` extension (for example, an image, a binary file, or any file under a dot-prefixed directory or dot-prefixed file such as `.git/` or `.obsidian/`)
> **When** the Owner runs any query
> **Then** the system never considers that file as a candidate match and never counts it toward the skipped-note total, because it was never a note to begin with
>
> — `spec.md §5, AC-10, verbatim` · full text: [spec.md](../spec.md)

## Checklist

- [ ] Define `Note` dataclass (`path`, `frontmatter`, `body`, `skip_reason`) in `src/kb/backends/markdown/note.py`
- [ ] Implement `parse_note(path: Path, notes_root: Path) -> Note`: read file, split `---`-delimited Frontmatter fence, `yaml.safe_load` it, set `skip_reason` on unreadable file / missing fence / YAML parse error / missing `title`+`summary`+`tags`
- [ ] Implement symlink check inside `parse_note` (or a sibling helper it calls): `Path.resolve()` the candidate path, set `skip_reason` when the resolved path is not `is_relative_to(notes_root)` or `resolve()` raises (loop)
- [ ] Ensure the caller-facing enumeration step (used by T5) filters out non-`.md` files and dot-prefixed paths *before* calling `parse_note` — those are never skip-counted (AC-10), so they must never produce a `Note` at all

## Edge cases

| Case | Behaviour |
|---|---|
| File unreadable (permissions error, invalid encoding) | `Note.skip_reason` set, `frontmatter=None`, note excluded from matching (AC-06) |
| Frontmatter fence missing entirely | `Note.skip_reason` set — treated as malformed, not "no frontmatter needed" |
| YAML syntax error inside the fence | `Note.skip_reason` set via caught `yaml.YAMLError` |
| Frontmatter parses but is missing `title`/`summary`/`tags` | `Note.skip_reason` set — per CONTEXT.md "Frontmatter ... NOT optional" |
| Symlink target outside notes root | `Note.skip_reason` set, never followed (AC-08) |
| Symlink that loops back on itself | `Note.skip_reason` set via caught resolution error (AC-08) |
| Symlink target inside notes root | Followed normally — `Note` built from the resolved content, no `skip_reason` |
| Non-`.md` file or dot-prefixed path | Never reaches `parse_note` — not a `Note`, not skip-counted (AC-10) |

## Definition of Done

- [ ] Unit tests for `parse_note` pass for: healthy note, unreadable file, missing fence, malformed YAML, missing required keys, symlink-outside, symlink-loop, symlink-inside
- [ ] Every Hard Rule inlined above still holds (symlink resolution, skip vs. not-a-note distinction)
- [ ] lint + vet clean
