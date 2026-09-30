"""Manifest-driven inclusion and ordering.

Provides POSITIVE selection.
"""

from __future__ import annotations

import json
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, Sequence


class ManifestRule:
    """
    .curate.json schema:

    {
      "include": ["src/a.py", "src/b.py"],
      "only_manifest": true
    }
    """

    def __init__(self) -> None:
        self._root: Path | None = None
        self._include: list[str] = []
        self._only: bool = False

    def prepare(self, *, root: Path) -> None:
        self._root = root
        mf = root / ".curate.json"  # kanske borde vara en config/constant
        if not mf.exists():
            return

        try:
            data = json.loads(mf.read_text())
        except Exception:
            return

        self._include = list(map(str, data.get("include", [])))
        self._only = bool(data.get("only_manifest", False))

    def allow(self, *, path: Path) -> bool | None:
        if not self._root or not self._include:
            return None

        try:
            rel = path.relative_to(self._root).as_posix()
        except Exception:
            return None

        if self._only:
            if path.is_dir():
                return None
            return False if rel not in self._include else None

        return None

    def order_children(
        self,
        *,
        parent: Path | None,
        children: Sequence[Path],
    ) -> Iterable[Path]:
        if not self._include:
            return children

        def rank(p: Path) -> tuple[int, str]:
            try:
                rel = p.relative_to(self._root).as_posix()  # type: ignore
            except Exception:
                return (10**9, p.name)

            if rel in self._include:
                return (self._include.index(rel), rel)
            return (10**9, rel)

        return sorted(children, key=rank)
