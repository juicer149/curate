"""
curate.facts — structural facts only (IR)

This module defines Curate’s core ontology.

Key idea:
    Curate does NOT understand meaning.
    It only records *what structural intervals exist and where*.

Invariant (critical):
    Scopes form a *laminar family*:
    any two scopes are either:
        - disjoint, or
        - nested (one fully contains the other)

This module must remain boring:
- immutable data
- no IO
- no caching
- no querying or relations
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional, Tuple, Union


@dataclass(frozen=True, slots=True)
class Scope:
    """
    Atomic structural interval.

    Fields:
        id:
            Unique identifier within a ScopeSet.
        parent_id:
            Parent scope id, or None if this is a root scope.
        kind:
            Upstream structural label (e.g. Tree-sitter node.type).
        start, end:
            1-based inclusive line span.
    """
    id: int
    parent_id: Optional[int]
    kind: str
    start: int
    end: int

    def contains(self, line: int) -> bool:
        """True iff `line` is within [start, end] (inclusive)."""
        return self.start <= line <= self.end


@dataclass(frozen=True, slots=True)
class ScopeSet:
    """
    Immutable collection of scopes.

    Properties:
        - scopes are laminar (nested or disjoint)
        - ordering is deterministic
        - safe to share across threads
        - equality is structural

    ScopeSet deliberately does NOT:
        - answer queries ("what is the parent?")
        - perform filtering
        - interpret scope kinds
        - understand files or projects
    """
    scopes: Tuple[Scope, ...]

    def __iter__(self) -> Iterator[Scope]:
        """Iterate over scopes in deterministic order."""
        return iter(self.scopes)

    def __len__(self) -> int:
        """Return number of scopes (O(1))."""
        return len(self.scopes)

    def __getitem__(self, index: Union[int, slice]) -> Union[Scope, "ScopeSet"]:
        """
        Index or slice into the ScopeSet.

        Semantics:
            - scopeset[i] returns the Scope at position i
            - scopeset[a:b] returns a new ScopeSet containing that slice

        Examples:
            scopeset[0]   -> Scope
            scopeset[-1]  -> Scope
            scopeset[1:4] -> ScopeSet
            scopeset[:]   -> ScopeSet
        """
        if isinstance(index, slice):
            return ScopeSet(self.scopes[index])
        return self.scopes[index]

    def __eq__(self, other: object) -> bool:
        """Structural equality: same scopes in the same order."""
        if not isinstance(other, ScopeSet):
            return NotImplemented
        return self.scopes == other.scopes

    @property
    def is_empty(self) -> bool:
        """True iff this ScopeSet contains no scopes."""
        return not self.scopes
