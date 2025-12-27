"""
Structural fact model (scope graph).

Prolog analogy
--------------
This module represents the *fact database*.

Each Scope corresponds to a fact of the form:

    scope(Id, ParentId, StartLine, EndLine, Role).

There are:
- no rules
- no queries
- no folding semantics

Why this exists
---------------
All intelligence in Curate operates *on top of* these facts.
This makes the system testable, composable, and extensible.

Design principle
----------------
"Facts are inert. Intelligence lives elsewhere."
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from .types import Role


@dataclass(frozen=True, slots=True)
class Scope:
    """
    A single structural scope in the source text.
    """

    id: int
    parent_id: Optional[int]
    start: int
    end: int
    role: Role

    @property
    def length(self) -> int:
        """Return the number of lines covered by this scope."""
        return self.end - self.start + 1


@dataclass(frozen=True, slots=True)
class ScopeGraph:
    """
    Immutable container for a laminär family of scopes.

    Invariant:
    - For any two scopes A and B:
        - A ⊂ B, or
        - B ⊂ A, or
        - A ∩ B = ∅
    """
    scopes: Tuple[Scope, ...]
