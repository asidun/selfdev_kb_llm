---
id: T8
title: "Integration tests: skip accounting, symlink escape/loop, non-md exclusion"
layer: "tests"
deps: ["T5"]
blocks: []
acs: ["AC-06", "AC-07", "AC-08", "AC-10"]
files_hint: ["tests/backends/test_markdown_backend.py"]
owner: "Andrii Sidun"
estimate: "M"
context_budget: "M"
status: "todo"
step: ""
---

# T8 — Integration tests: skip accounting, symlink escape/loop, non-md exclusion

## Place in the sequence

- **Blocked by:** T5 — Wire MarkdownBackend.query() pipeline · **Blocks:** none · **Wave:** 4 (parallel with T6, T9; shares a lane with T7).
- **Lane:** shares `tests/backends/test_markdown_backend.py` with T7 — serialized (both append to the same new test file).

## Why (user story)

> **As an** Owner
> **I want** to see how many notes were skipped because they couldn't be read or parsed
> **So that** I can tell "the knowledge base has no answer" apart from "the knowledge base silently ignored a note that might have had the answer"
>
> — `spec.md §4, US-06, verbatim` · full text: [spec.md](../spec.md)

This task proves the NFR "0 notes ever excluded from an answer without being counted in the skipped total" (spec §6) and AC-08/AC-10's filesystem-trust boundaries, against a real temp-dir fixture.

## Inlined context

> - A malformed note — missing frontmatter delimiter, or invalid YAML — to assert skip accounting (AC-06) and that healthy notes still match around it (AC-07).
> - A note under a dot-prefixed directory (e.g. `.obsidian/`) and a non-`.md` file, to assert neither is counted toward matches or the skipped total (AC-10).
> - A symlink inside the notes root resolving outside it, and a self-looping symlink, to assert AC-08's reject-and-count behavior; a symlink resolving to a target still inside the notes root, to assert it is followed normally.
>
> — `data-model.md §Test fixtures, verbatim` · full text: [data-model.md](../data-model.md)

> Correctness — no silent note loss | 0 notes ever excluded from an answer without being counted in the skipped total (AC-06) | assertion in the test suite against a fixture containing ≥1 malformed note
>
> — `spec.md §6, NFR table row, verbatim` · full text: [spec.md](../spec.md)

**Fallback:** insufficient or contradicted by the code → read [data-model.md](../data-model.md) §Test fixtures and [sad.md](../sad.md) §6 flows 4–5 in full and follow them. Do not guess.

## Data delta

No DB changes — tests build `tmp_path` fixtures only, nothing persisted.

## API contract

Internal — tests call `MarkdownBackend.query(text)` directly. CLI-level skip-count surfacing is fixed in `contracts/cli.md` §Behavior matrix row "Query matches ≥1 note, ≥1 note skipped elsewhere."

## Acceptance criteria

### AC-06 — domain invariant

> **Given** the notes root contains a note the system cannot read as a file (for example, a permissions error or invalid encoding), or whose Frontmatter block is missing or cannot be parsed (for example, broken YAML, or a missing title/summary/tags block)
> **When** the Owner runs any query
> **Then** the system never silently drops that note from consideration — it always counts it as skipped, excludes it entirely from matching, and reports the skipped count in the answer, so a skipped note is never indistinguishable from "no matches"
>
> — `spec.md §5, AC-06, verbatim` · full text: [spec.md](../spec.md)

### AC-07 — domain invariant

> **Given** one note under the notes root is unreadable as a file, or has a missing or malformed Frontmatter block (as defined in AC-06)
> **When** the Owner runs a query that would otherwise match other, healthy notes
> **Then** the system still returns those other matches — one broken note never prevents the whole query from answering
>
> — `spec.md §5, AC-07, verbatim` · full text: [spec.md](../spec.md)

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

- [ ] Add to `tests/backends/test_markdown_backend.py` (shared with T7; coordinate file layout)
- [ ] `test_malformed_note_skipped_and_counted` — AC-06: invalid YAML note, assert `Answer.text` reports skipped count, note excluded from `sources`
- [ ] `test_unreadable_file_skipped_and_counted` — AC-06: a file with no read permission (or invalid encoding bytes), same assertions
- [ ] `test_healthy_notes_still_match_around_broken_one` — AC-07: malformed note + healthy matching note in the same root, assert the healthy note's match is still returned
- [ ] `test_symlink_escaping_root_rejected_and_counted` — AC-08: symlink inside notes root pointing outside it, assert excluded + skip-counted
- [ ] `test_symlink_loop_rejected_and_counted` — AC-08: self-referential symlink, assert excluded + skip-counted, no infinite loop / crash
- [ ] `test_symlink_inside_root_followed_normally` — AC-08: symlink resolving inside notes root, assert it is searched and can match like a normal note
- [ ] `test_non_md_file_and_dot_path_never_counted` — AC-10: a non-`.md` file and a note under `.obsidian/`, assert neither appears in matches nor increments the skipped count (assert skipped count unaffected by their presence)

## Edge cases

| Case | Behaviour |
|---|---|
| All notes in the root are malformed (0 healthy) | `Answer.text` = "no matching notes" (AC-04) + full skipped count — not an error |
| Symlink target doesn't exist at all (broken link, not an escape) | Treated as unreadable → skip-counted (AC-06), consistent with "cannot be read as a file" |
| Multiple skip reasons present simultaneously (malformed note + escaping symlink + non-md file) | Skipped count reflects only the malformed note + the symlink (2); the non-md file contributes 0 (AC-10) |

## Definition of Done

- [ ] All checklist tests pass against the T5 implementation
- [ ] The NFR assertion ("0 notes ever excluded without being counted") is directly tested, not just implied
- [ ] No mocking of the filesystem — real `tmp_path` fixtures (incl. real `os.symlink` calls) only
- [ ] lint + vet clean
