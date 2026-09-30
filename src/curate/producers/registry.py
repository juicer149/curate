# curate/producers/registry.py
from __future__ import annotations

from typing import Callable, Dict, Protocol

from ..facts import RawFactSet


class Producer(Protocol):
    def __call__(self, *, source: str, language: str) -> RawFactSet:
        ...


Factory = Callable[[], Producer]

PRODUCERS: Dict[str, Factory] = {}


def register(name: str, factory: Factory) -> None:
    """
    Register a producer factory under a name.

    Notes:
        - This is a convenience API for adapters living in other packages.
        - Registration is global within the process.
        - Curate core remains stateless; this is merely a name -> factory map.
    """
    if not name:
        raise ValueError("producer name must be non-empty")
    PRODUCERS[name] = factory


def _noop() -> Producer:
    from .noop import build_raw_facts

    return build_raw_facts


PRODUCERS.setdefault("noop", _noop)
