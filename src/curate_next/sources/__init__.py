"""
curate_core.sources — source normalization layer

Converts various external origins into source text.

This layer:
- is orthogonal to filesystem structure
- is orthogonal to language detection
- is orthogonal to parsing
- is orthogonal to address assignment

Think of this as:
    origin → text
"""

from .protocol import SourceBackend
from .registry import SOURCE_BACKENDS
from .compose import compose_source


def _string() -> SourceBackend:
    from .backends.string import StringSource
    return StringSource()


def _file() -> SourceBackend:
    from .backends.file import FileSource
    return FileSource()


SOURCE_BACKENDS.setdefault("string", _string)
SOURCE_BACKENDS.setdefault("file", _file)

__all__ = [
    "SourceBackend",
    "SOURCE_BACKENDS",
    "compose_source",
]
