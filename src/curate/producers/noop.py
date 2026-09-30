from __future__ import annotations
from ..facts import RawFactSet


def build_raw_facts(*, source: str, language: str) -> RawFactSet:
    """
    No-op producer.

    Contract:
        - Never raises
        - Emits no structure
    """
    return RawFactSet.from_iter(())
