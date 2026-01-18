"""curate.facts — structural ontology (facts only)

This module defines Curate’s entire data model.

Rules:
- immutable
- no I/O
- no interpretation
- no queries
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Iterable, Union, TypeAlias

ScopeId: TypeAlias = Tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Scope:
    """
    Atomic structural fact.

    Fields:
        id:
            Hierarchical structural address.
            Parent is id[:-1].

        kind:
            Syntax node type (verbatim from Tree-sitter).

        start, end:
            1-based inclusive line span.

    Invariants:
        - id is non-empty
        - start <= end
    """
    id: ScopeId
    kind: str
    start: int
    end: int

    def contains(self, line: int) -> bool:
        return self.start <= line <= self.end

    @property
    def parent_id(self) -> ScopeId | None:
        return self.id[:-1] if len(self.id) > 1 else None


@dataclass(frozen=True, slots=True)
class ScopeSet:
    """
    Immutable collection of Scope facts.

    Guarantees:
    - deterministic ordering
    - laminar structure
    - no semantic meaning

    ScopeSet has NO query logic.
    """
    scopes: Tuple[Scope, ...]

    def __iter__(self) -> Iterable[Scope]:
        return iter(self.scopes)

    def __len__(self) -> int:
        return len(self.scopes)

    def __getitem__(self, item: Union[int, slice]) -> Union[Scope, "ScopeSet"]:
        if isinstance(item, slice):
            return ScopeSet(self.scopes[item])
        return self.scopes[item]
