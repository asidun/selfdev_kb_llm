from kb.backends.vector.chroma_store import ChromaStore


def test_chroma_store_empty_query_returns_no_results(tmp_path):
    store = ChromaStore(persist_dir=tmp_path / "chroma")
    assert store.query("anything") == []


def test_chroma_store_reindex_then_query_finds_note(tmp_path):
    notes_root = tmp_path / "notes"
    notes_root.mkdir()
    (notes_root / "note1.md").write_text("Chroma is a local vector database.", encoding="utf-8")

    store = ChromaStore(persist_dir=tmp_path / "chroma")
    count = store.reindex(notes_root)
    assert count == 1

    results = store.query("vector database")
    assert len(results) == 1
    assert "note1.md" in results[0].source
