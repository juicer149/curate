"""
Minimal .gitignore support (best-effort).
"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, Sequence


class GitIgnoreRule:
    def __init__(self) -> None:
        self._root: Path | None = None
        self._patterns: list[str] = []

    def prepare(self, *, root: Path) -> None:
        self._root = root
        gi = root / ".gitignore"
        if not gi.exists():
            return

        try:
            for line in gi.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                self._patterns.append(line)
        except Exception:
            pass

    def allow(self, *, path: Path) -> bool | None:
        if not self._patterns or not self._root:
            return None
        try:
            rel = path.relative_to(self._root).as_posix()
        except Exception:
            return None

        for pat in self._patterns:
            if fnmatch(rel, pat):
                return False
        return None

    def order_children(
        self,
        *,
        parent: Path | None,
        children: Sequence[Path],
    ) -> Iterable[Path]:
        return children
