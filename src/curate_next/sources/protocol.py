"""curate_core.sources.protocol — source backend contract

Defines the minimal contract for converting an external origin
into a source string.

Responsibilities:
- define the callable interface for source backends
- enforce a string-only output contract

Non-responsibilities:
- no address handling
- no language detection
- no parsing
- no filesystem traversal
- no caching

Invariants:
- MUST NOT raise uncaught exceptions
- MUST return a string (possibly empty)
- MUST be deterministic for the same input
"""

from __future__ import annotations
from typing import Protocol, Mapping, Any


class SourceBackend(Protocol):
    """
    Source backend protocol.

    A backend converts a backend-specific specification
    into a source string.

    The spec MUST be:
    - pure data (dict-like)
    - serializable
    - side-effect free
    """

    def read(self, *, spec: Mapping[str, Any]) -> str:
        """
        Read and return source text.

        Implementations MUST:
        - never raise to caller
        - return "" on failure
        """
        ...

