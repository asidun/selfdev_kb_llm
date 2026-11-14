from __future__ import annotations

from pathlib import Path

from kb.core.knowledge_base import Answer


class MarkdownBackend:
    """Direct markdown-file read, no embeddings (Karpathy-style)."""

    def __init__(self, notes_root: Path):
        self._notes_root = notes_root

    def query(self, text: str) -> Answer:
        if not self._notes_root.exists():
            return Answer(text=f"notes root {self._notes_root} does not exist", sources=[])
        matches = []
        needle = text.lower()
        for path in sorted(self._notes_root.rglob("*.md")):
            content = path.read_text(encoding="utf-8")
            if needle in content.lower():
                matches.append(path)
        if not matches:
            return Answer(text="no matching notes found", sources=[])
        excerpts = "\n\n".join(p.read_text(encoding="utf-8") for p in matches)
        return Answer(text=excerpts, sources=[str(p) for p in matches])
