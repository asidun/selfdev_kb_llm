from __future__ import annotations

import typer

from kb.backends.markdown.backend import MarkdownBackend
from kb.backends.vector.backend import VectorBackend
from kb.config.settings import load_settings
from kb.core.knowledge_base import KbError, KnowledgeBase

app = typer.Typer(help="Personal knowledge-base CLI: markdown read or vector RAG, per query.")


def _build_kb() -> KnowledgeBase:
    settings = load_settings()
    return KnowledgeBase(
        {
            "markdown": MarkdownBackend(settings.notes_root),
            "vector": VectorBackend(settings.notes_root, settings.vector_persist_dir),
        }
    )


@app.command()
def query(text: str, mode: str = typer.Option("markdown", help="markdown | vector")) -> None:
    """Query the knowledge base, choosing the backend for this call."""
    kb = _build_kb()
    try:
        answer = kb.query(text, mode)
    except KbError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(answer.text)


@app.command()
def reindex() -> None:
    """Rebuild the vector index from the markdown notes (manual, v1)."""
    settings = load_settings()
    backend = VectorBackend(settings.notes_root, settings.vector_persist_dir)
    count = backend.reindex()
    typer.echo(f"reindexed {count} notes")


if __name__ == "__main__":
    app()
