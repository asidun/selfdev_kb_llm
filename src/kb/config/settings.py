from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    notes_root: Path
    default_mode: str = "markdown"
    vector_persist_dir: Path | None = None


def load_settings() -> Settings:
    notes_root = Path(os.environ.get("KB_NOTES_ROOT", "~/kb-notes")).expanduser()
    vector_dir = os.environ.get("KB_VECTOR_DIR")
    return Settings(
        notes_root=notes_root,
        default_mode=os.environ.get("KB_DEFAULT_MODE", "markdown"),
        vector_persist_dir=Path(vector_dir).expanduser() if vector_dir else None,
    )
