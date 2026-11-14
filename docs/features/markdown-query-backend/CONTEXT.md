---
status: Living
updated_at: "2026-11-14"
---

# Domain Context — markdown-query-backend

## Glossary

- Excerpt — the focused snippet of text around a match, bounded to a paragraph/block, returned to the caller instead of the whole note content. NOT the frontmatter summary field — an excerpt is query-specific extracted text, not author-written.
- Frontmatter — the required structured header block (title, summary, tags) at the top of every note; a note whose Frontmatter alone contains every significant word of the query ranks above a note that only reaches a full match via its body. NOT optional — a note missing it, or whose Frontmatter block cannot be parsed, is treated as unreadable and skipped (not searched), per AC-06.
- Match — a note whose frontmatter or body content contains every significant word of the query, eligible to appear in query results. NOT an exact-phrase match — matching is word-presence based, not literal substring equality.
