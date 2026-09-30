"""
curate_next.facts — raw facts and derived facts

We deliberately separate two levels:

RawScope (producer output)
--------------------------
A producer reports only:
- label
- start/end Position (row + optional col)
- optional meta payload

No laminarity guarantees. No address. No root requirement.

Scope (core output)
-------------------
Core derives:
- deterministic laminar structure (LINE-based)
- Address assignment (0..k-1 per parent, no gaps)
- always a root "module" scope at Address.root()

Important
---------
Core's laminar policy is line-based by design.
Column precision and other payload may be carried via meta for higher layers,
but core does not interpret it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, Mapping, Tuple

from .address import Address


# -----------------------------
# Raw layer
# -----------------------------


@dataclass(frozen=True, slots=True)
class Position:
    """
    Source position.

    - row is inclusive, 1-based
    - col is optional and producer-defined (core does not interpret it)
    """

    row: int
    col: int | None = None

    def with_row(self, row: int) -> "Position":
        return Position(row=int(row), col=self.col)


@dataclass(frozen=True, slots=True)
class RawScope:
    """
    Producer output fact.

    Producers MUST NOT assign addresses or depend on core laminar policy.
    """

    label: str
    start: Position
    end: Position
    meta: Mapping[str, Any] = field(default_factory=dict)

    @property
    def start_line(self) -> int:
        return int(self.start.row)

    @property
    def end_line(self) -> int:
        return int(self.end.row)


class RawScopeSet:
    """Immutable collection of RawScope."""

    def __init__(self, scopes: Iterable[RawScope]):
        self._items = tuple(scopes)

    def __iter__(self) -> Iterator[RawScope]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, i: int) -> RawScope:
        return self._items[i]

    def items(self) -> Tuple[RawScope, ...]:
        return self._items


# -----------------------------
# Derived layer
# -----------------------------


@dataclass(frozen=True, slots=True)
class Scope:
    """
    Derived laminar scope (room), line-based.

    Invariants guaranteed by derive:
    - address is unique
    - addresses are contiguous per parent (0..k-1, no gaps)
    - start/end are valid inclusive 1-based LINE spans within document bounds
    - siblings do not overlap by LINE geometry (laminar)
    """

    address: Address
    label: str
    start: int
    end: int
    meta: Mapping[str, Any] = field(default_factory=dict)

    @property
    def parent_address(self) -> Address | None:
        return self.address.parent


class ScopeSet:
    """
    Derived region of scopes.

    Ordering is deterministic by geometry, not producer order:
        (start asc, end desc, label asc, address)
    """

    def __init__(self, scopes: Iterable[Scope]):
        items = tuple(scopes)
        items = tuple(sorted(items, key=lambda s: (s.start, -s.end, s.label, s.address.parts)))

        index: Dict[Tuple[int, ...], Scope] = {}
        for s in items:
            # Core should guarantee uniqueness; we keep this total:
            # "first wins" deterministically because items is sorted.
            index.setdefault(s.address.parts, s)

        self._items = items
        self._index = index

    def __iter__(self) -> Iterator[Scope]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, i: int) -> Scope:
        return self._items[i]

    def by_address(self, addr: Address) -> Scope | None:
        return self._index.get(addr.parts)

    def has_child0(self, addr: Address) -> bool:
        """Fast 'has any children' check, valid because core assigns contiguous children."""
        return (addr + 0).parts in self._index

    def children_addresses(self, addr: Address) -> Tuple[Address, ...]:
        """
        Enumerate child addresses (0..k-1) until first miss.

        Safe because core assigns children contiguously with no gaps.
        """
        out = []
        i = 0
        while True:
            child = addr + i
            if child.parts not in self._index:
                break
            out.append(child)
            i += 1
        return tuple(out)

    def index(self) -> Mapping[Tuple[int, ...], Scope]:
        return self._index
