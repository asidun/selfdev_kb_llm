from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VectorResult:
    text: str
    source: str


class ChromaStore:
    """Thin VectorStore-port adapter over a local embedded Chroma collection."""

    COLLECTION_NAME = "kb_notes"

    def __init__(self, persist_dir: Path | None = None):
        import chromadb

        if persist_dir is not None:
            self._client = chromadb.PersistentClient(path=str(persist_dir))
        else:
            self._client = chromadb.Client()
        self._collection = self._client.get_or_create_collection(self.COLLECTION_NAME)

    @staticmethod
    def _chunk_id(note_path: Path, content: str) -> str:
        digest = hashlib.sha256((str(note_path) + content).encode("utf-8")).hexdigest()
        return digest

    def reindex(self, notes_root: Path) -> int:
        if not notes_root.exists():
            return 0
        count = 0
        for path in sorted(notes_root.rglob("*.md")):
            content = path.read_text(encoding="utf-8")
            chunk_id = self._chunk_id(path, content)
            self._collection.upsert(
                ids=[chunk_id],
                documents=[content],
                metadatas=[{"source": str(path)}],
            )
            count += 1
        return count

    def query(self, text: str, n_results: int = 5) -> list[VectorResult]:
        if self._collection.count() == 0:
            return []
        result = self._collection.query(query_texts=[text], n_results=n_results)
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        return [
            VectorResult(text=doc, source=meta.get("source", ""))
            for doc, meta in zip(documents, metadatas)
        ]
