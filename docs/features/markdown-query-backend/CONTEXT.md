---
status: Living
updated_at: "2026-11-14"
---

# Domain Context — markdown-query-backend

## Glossary

- Excerpt — the focused snippet of text around a match, bounded to a paragraph/block, returned to the caller instead of the whole note content. NOT the frontmatter summary field — an excerpt is query-specific extracted text, not author-written.
- Frontmatter — the optional structured header block (title, summary, tags) at the top of a note; when present, a query match there ranks above a body-only match. NOT a hard requirement — a note without it is still searched, just without the ranking boost.
- Match — a note whose frontmatter or body content contains every significant word of the query, eligible to appear in query results. NOT an exact-phrase match — matching is word-presence based, not literal substring equality.
