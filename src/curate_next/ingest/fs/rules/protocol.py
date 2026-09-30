"""
curate_core.ingest.fs.rules.protocol

Protocol for filesystem selection and ordering rules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Protocol, Sequence


class PathRule(Protocol):
    """
    Filesystem policy rule.

    Contract:
    - MUST NOT raise (adapter enforces totality)
    - allow():
        False → exclude
        None / True → allow
    - order_children():
        must be deterministic and stable
    """

    def prepare(self, *, root: Path) -> None:
        ...

    def allow(self, *, path: Path) -> bool | None:
        ...

    def order_children(
        self,
        *,
        parent: Path | None,
        children: Sequence[Path],
    ) -> Iterable[Path]:
        ...
