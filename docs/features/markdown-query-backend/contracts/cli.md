---
status: Draft
owner: "Andrii Sidun"
reviewers: []
updated_at: "2026-11-14"
feature_size: "S"
---

# CLI contract — markdown-query-backend

Interface kind: `cli` (`sad.md` frontmatter `target_surfaces: ["cli"]` — CLI-only product, `CLAUDE.md`
"CLI-only — no HTTP/MCP server"). Derived from `data-model.md` (`Note`, `Answer` shapes) +
`sad.md` §6 sequences (flows 1-5) + `spec.md` §4/§5 (user stories, acceptance criteria). No new
command or flag is introduced by this feature — `kb query` and its `--mode` option already exist
(`src/kb/cli/main.py`); this contract fixes the **observable behavior** of `--mode markdown`
(stdout/stderr shape, exit codes) that the feature's acceptance criteria require but the current
placeholder stub does not satisfy.

## Command: `kb query`

```
kb query TEXT [--mode markdown|vector]
```

| Element | Type | Constraint | Origin |
|---|---|---|---|
| `TEXT` (positional arg) | `str` | rejected when blank/whitespace-only (AC-05) | existing CLI signature (`src/kb/cli/main.py`); constraint added by AC-05 |
| `--mode` | `str` | `markdown` (default) \| `vector` | existing CLI signature; unchanged by this feature |

This feature only changes behavior when `--mode markdown` (the default). `--mode vector` is out of
scope (roadmap step 3).

## Behavior matrix

One row per `sad.md` §6 flow / `spec.md` AC. `stdout`/`stderr` show the shape of
`Answer.text`/the error message, not literal fixed text (exact wording is an implementation detail
per ADR-0001 "Neutral" consequence) — placeholders are marked `<...>`.

| Scenario | AC / flow | stdout | stderr | Exit code |
|---|---|---|---|---|
| Query matches ≥1 note, no skips | AC-01, AC-02, AC-02b, AC-03, AC-03b; flow 1 | ranked, excerpted matches (≤ top 10, Frontmatter-complete bucket first, path-order tiebreak within a bucket; each excerpt ≤ ~5 block-aware lines) | — | 0 |
| Query matches ≥1 note, ≥1 note skipped elsewhere in the notes root | AC-06, AC-07; flow 4 | same as above, **plus** a trailing plain-text line reporting the skipped-note count (`sad.md` §8 "Result surfacing"; exact wording is an open question until this contract — see Field origins below) | — | 0 |
| No note matches | AC-04; flow 3 (else-branch) | explicit "no matching notes" message | — | 0 |
| Blank/whitespace-only `TEXT` | AC-05; flow 3 (alt-branch) | — | one-line message explaining search terms are required | 1 |
| Configured notes root missing or unreadable | AC-04b; flow 2 | — | one-line message distinguishing this from "no matching notes" | 1 |
| Symlink escaping the notes root, or a self-loop, present under the notes root | AC-08; flow 5 | linked note's content is excluded from the answer; the linked note is counted toward the skipped total like any other skip (AC-06) — same stdout shape as the "query matches, with skips" row | — | 0 |
| Non-`.md` file, or any file under a dot-prefixed path, present under the notes root | AC-10 | neither a candidate match nor counted toward skipped — invisible to the answer entirely | — | 0 |

## Error codes

Both are raised once per call as a `KbError` subclass (`CLAUDE.md` "Errors": single hierarchy,
caught once at the CLI top, one stderr line, non-zero exit — already implemented in
`src/kb/cli/main.py`'s `except KbError` block, reused verbatim per ADR-0001).

| Error type | Raised when | HTTP-contract analogue | Exit code |
|---|---|---|---|
| `NotesRootError(KbError)` | configured notes root does not exist or cannot be read (AC-04b, ADR-0001) | `config.notes_root_invalid` | 1 |
| `BlankQueryError(KbError)` | `TEXT` is blank or whitespace-only (AC-05) | `query.blank_text` | 1 |

Per-note failures (unreadable file, missing/malformed Frontmatter, escaping/looping symlink;
AC-06/AC-07/AC-08) are **never** raised — they are counted in the skipped total and folded into a
normal `Answer`, not an error (`sad.md` §8 "Error handling" row).

## Output text shape (`Answer.text`)

Traced to `data-model.md`'s `Answer` shape (unchanged 2-field dataclass; sad.md §1 decision override).

```
<ranked excerpt 1>

<ranked excerpt 2>

...

<trailing skipped-count line, only when skipped > 0>
```

- Each excerpt is bounded to ~5 lines of block-aware context around the passage with the most
  significant-word hits (`sad.md` §8 "Excerpting"); never splits a fenced code block or table row
  (AC-03).
- At most 10 ranked excerpts per answer (`sad.md` §8 "Excerpting"; AC-03b).
- `Answer.sources` carries the same matching notes' paths, in the same rank order, for any caller
  that wants structured access rather than parsing `.text` (unchanged `data-model.md` shape).

## Examples

**Match with no skips:**

```
$ kb query "how do I renew a TLS certificate" --mode markdown
## infra/tls-renewal.md
Renewing the TLS certificate requires rotating the ACME account key first...

$ echo $?
0
```

**Match with skips:**

```
$ kb query "deployment checklist" --mode markdown
## ops/deploy-checklist.md
Before any deploy, confirm the staging smoke test passed...

1 note skipped (unreadable or malformed frontmatter)

$ echo $?
0
```

**No match:**

```
$ kb query "quantum entanglement" --mode markdown
no matching notes found

$ echo $?
0
```

**Blank query:**

```
$ kb query "   " --mode markdown
error: search terms are required

$ echo $?
1
```

**Bad notes root:**

```
$ kb query "anything" --mode markdown
error: notes root <path> does not exist or cannot be read

$ echo $?
1
```
