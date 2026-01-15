# src/curate/model.py
"""
Structural data model.

This module defines *what exists*, not *how it is queried*.

Everything here should be:
- Immutable
- Simple
- Free of policy
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True, slots=True)
class Scope:
    """
    Atomic structural fact about a source file.

    A scope represents a contiguous, named region of source code
    such as a function, class, or control block.

    Invariants:
    - start/end are 1-based inclusive
    - header_lines >= 1
    """
    id: int
    parent_id: Optional[int]
    kind: str
    start: int
    end: int
    header_lines: int = 1

    def contains_line(self, line: int) -> bool:
        """
        Check if a line number falls within this scope.
        """
        return self.start <= line <= self.end

    @property
    def length(self) -> int:
        """
        Total number of lines spanned by this scope.
        """
        return self.end - self.start + 1

    def header_range(self) -> tuple[int, int]:
        """
        Return the header portion of this scope.

        Pseudocode:
        - header starts at scope.start
        - header spans header_lines
        - clipped to scope.end
        """
        a = self.start
        b = min(self.end, self.start + max(1, int(self.header_lines)) - 1)
        return (a, b)

    def body_range(self) -> tuple[int, int] | None:
        """
        Return the body portion of this scope, if any.

        Pseudocode:
        - body starts after header
        - body ends at scope.end
        - return None if no body exists
        """
        a = self.start + max(1, int(self.header_lines))
        b = self.end
        return (a, b) if a <= b else None


@dataclass(frozen=True, slots=True)
class ScopeGraph:
    """
    Immutable collection of scopes.

    Producer responsibility:
    - scopes must form a laminar family
      (nested or disjoint, never partially overlapping)
    """
    scopes: Tuple[Scope, ...]
