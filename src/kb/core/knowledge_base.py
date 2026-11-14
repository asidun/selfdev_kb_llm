from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class KbError(Exception):
    """Base for every error raised across kb modules."""


class UnknownBackendError(KbError):
    pass


@dataclass
class Answer:
    text: str
    sources: list[str]


class Backend(Protocol):
    def query(self, text: str) -> Answer: ...


class KnowledgeBase:
    """Routes a query to the backend selected for that single call."""

    def __init__(self, backends: dict[str, Backend]):
        self._backends = backends

    def query(self, text: str, mode: str) -> Answer:
        try:
            backend = self._backends[mode]
        except KeyError:
            raise UnknownBackendError(
                f"unknown backend {mode!r}; available: {sorted(self._backends)}"
            ) from None
        return backend.query(text)
