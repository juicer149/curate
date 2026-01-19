"""curate.facts — structural ontology (facts only)

This module defines Curate’s entire data model.

Rules:
- immutable
- no I/O
- no interpretation
- no queries

Facts describe *where structure exists*, not what it means.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Iterable, Union, TypeAlias


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

ScopeAddress: TypeAlias = Tuple[int, ...]


# ---------------------------------------------------------------------------
# Core facts
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Scope:
    """
    Atomic structural fact.

    A Scope represents a contiguous structural region in source text.

    Fields:
        address:
            Hierarchical structural address (postal-code style).

            Each element refines the region:
            - earlier elements describe broader structural areas
            - later elements narrow the region
            - the full address identifies the smallest structural unit
              represented by this scope

            The parent address is always:
                address[:-1]

            An address is not an identity and carries no semantic meaning.
            It is meaningful only within its structural context.

        label:
            Syntax node type, producer-defined and verbatim
            (e.g. Tree-sitter node.type).

        start, end:
            1-based inclusive line span.

    Invariants:
        - address is non-empty
        - start <= end
    """

    address: ScopeAddress
    label: str
    start: int
    end: int

    def contains(self, line: int) -> bool:
        """Return True if the given line is within this scope."""
        return self.start <= line <= self.end

    @property
    def parent_address(self) -> ScopeAddress | None:
        """Return the parent structural address, or None if this is root."""
        return self.address[:-1] if len(self.address) > 1 else None


@dataclass(frozen=True, slots=True)
class ScopeSet:
    """
    Immutable collection of Scope facts.

    Guarantees:
    - deterministic ordering
    - laminar structure
    - no semantic meaning

    ScopeSet deliberately exposes no query logic.
    Structural relations are derived algebraically from Scope.address.
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
