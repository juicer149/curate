"""
Exclude common binary artifacts by suffix.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence


_BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".pdf",
    ".zip", ".tar", ".gz", ".xz", ".7z",
    ".exe", ".dll", ".so",
    ".pyc", ".class",
}


class BinaryRule:
    def prepare(self, *, root: Path) -> None:
        return

    def allow(self, *, path: Path) -> bool | None:
        if path.is_dir():
            return None
        return False if path.suffix.lower() in _BINARY_SUFFIXES else None

    def order_children(
        self,
        *,
        parent: Path | None,
        children: Sequence[Path],
    ) -> Iterable[Path]:
        return children
