from __future__ import annotations

"""
Structural fact model (scope graph).

This module contains *inert facts only*:
- No parsing
- No traversal
- No folding semantics

A ScopeGraph is a laminar family of scopes.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from .types import Role


@dataclass(frozen=True, slots=True)
class Scope:
    """
    A structural scope in source text.

    start/end: 1-based inclusive line span
    header_lines: number of leading lines that must remain visible (>=1)
    """

    id: int
    parent_id: Optional[int]
    kind: str
    start: int
    end: int
    role: Role
    header_lines: int = 1

    @property
    def length(self) -> int:
        return self.end - self.start + 1

    @property
    def body_start(self) -> int:
        """First line of the foldable body."""
        return self.start + self.header_lines

    def contains_line(self, line: int) -> bool:
        return self.start <= line <= self.end


@dataclass(frozen=True, slots=True)
class ScopeGraph:
    """
    Immutable container for a laminar family of scopes.
    """

    scopes: Tuple[Scope, ...]
