"""curate_core.sources.compose — source composition helper

Provides a single, boring helper for:
- backend lookup
- safe invocation
- total behavior

This is the ONLY place where:
- registry lookup
- fallback-to-empty
- call discipline
are combined.

Responsibilities:
- compose (kind, spec) -> source string
- guarantee totality

Non-responsibilities:
- no caching
- no language detection
- no address logic
- no filesystem traversal beyond backend

Invariants:
- never raises
- always returns a string
"""

from __future__ import annotations
from typing import Mapping, Any

from .registry import SOURCE_BACKENDS


def compose_source(*, kind: str, spec: Mapping[str, Any]) -> str:
    """
    Compose a source string from a backend kind and spec.

    If backend is missing or fails:
        -> return empty string
    """
    factory = SOURCE_BACKENDS.get(kind)
    if factory is None:
        return ""

    try:
        backend = factory()
        return backend.read(spec=spec)
    except Exception:
        # Defensive: should not happen if backends obey contract
        return ""
