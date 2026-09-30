"""
curate_core.sources.backends.string — in-memory source backend

Responsibilities:
- return source text from an explicit string

Non-responsibilities:
- no validation
- no parsing
- no encoding concerns

Invariants:
- missing or invalid input -> empty string
"""

from __future__ import annotations
from typing import Mapping, Any


class StringSource:
    """
    Source backend for in-memory strings.
    """

    def read(self, *, spec: Mapping[str, Any]) -> str:
        try:
            return str(spec.get("text", ""))
        except Exception:
            return ""
