"""
curate_core.sources.backends.file — filesystem source backend

Responsibilities:
- read UTF-8 text from a filesystem path
- degrade gracefully on errors

Non-responsibilities:
- no path discovery
- no language detection
- no caching
- no directory traversal

Invariants:
- invalid or unreadable path -> empty string
"""

from __future__ import annotations
from pathlib import Path
from typing import Mapping, Any


class FileSource:
    """
    Source backend for filesystem files.
    """

    def read(self, *, spec: Mapping[str, Any]) -> str:
        try:
            path = spec.get("path")
            if not isinstance(path, Path):
                return ""

            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
