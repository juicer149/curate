"""
Normalization layer.

Why this exists
---------------
Editors expect stable, ordered ranges.

This module enforces that contract.
"""

from __future__ import annotations
from .types import Range


def normalize(ranges: set[Range]) -> tuple[Range, ...]:
    return tuple(sorted(ranges))
