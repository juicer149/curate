"""
Source acquisition layer.

This module loads source text and nothing else.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceFile:
    """
    Represents a loaded source file.

    Attributes:
        path: Path to the source file
        content: Raw text content
    """
    path: Path
    content: str


def load_source(path: str) -> SourceFile:
    """
    Load a file from disk.

    v0.1:
      - expects local files
      - intended primarily for .py
    """
    p = Path(path)
    return SourceFile(path=p, content=p.read_text(encoding="utf-8"))
