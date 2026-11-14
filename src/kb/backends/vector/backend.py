from __future__ import annotations

from pathlib import Path

from kb.core.knowledge_base import Answer


class VectorBackend:
    """RAG retrieval over a pluggable vector store (Chroma first)."""

    def __init__(self, notes_root: Path, persist_dir: Path | None = None):
        self._notes_root = notes_root
        self._persist_dir = persist_dir
        self._store = None

    def _ensure_store(self):
        if self._store is None:
            from kb.backends.vector.chroma_store import ChromaStore

            self._store = ChromaStore(persist_dir=self._persist_dir)
        return self._store

    def query(self, text: str) -> Answer:
        store = self._ensure_store()
        results = store.query(text)
        if not results:
            return Answer(text="no matching notes found", sources=[])
        excerpts = "\n\n".join(r.text for r in results)
        return Answer(text=excerpts, sources=[r.source for r in results])

    def reindex(self) -> int:
        store = self._ensure_store()
        return store.reindex(self._notes_root)
