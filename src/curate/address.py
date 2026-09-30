# curate/address.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, slots=True)
class Address:
    """
    Structural coordinate in a tree-shaped space.

    An Address represents a position in a hierarchy using prefix-based
    path encoding. Hierarchy is not stored explicitly; it emerges from
    relations between addresses.

    Conceptually similar to outline or proposition numbering
    (e.g. 1, 1.1, 1.2, 1.2.1), filesystem paths, or other
    prefix-based addressing schemes, where hierarchy is implied
    by shared prefixes rather than stored explicitly.


    Role:
        - Encode hierarchy purely via prefix algebra
        - Carry no pointers, parent links, or stored relations
        - Remain independent of syntax, language, or semantics

    Invariants:
        - The empty address () represents the root
        - Address components are non-negative integers
        - Parent–child relations are defined by prefix structure
        - Addresses are immutable value objects
    """

    parts: Tuple[int, ...]

    def __post_init__(self) -> None:
        for p in self.parts:
            if not isinstance(p, int) or p < 0:
                raise ValueError(f"invalid address component: {p!r}")

    @staticmethod
    def root() -> "Address":
        """
        Return the root address.
        """
        return Address(())

    @property
    def parent(self) -> "Address | None":
        """
        Return the parent address, or None if this is the root.
        """
        if not self.parts:
            return None
        return Address(self.parts[:-1])

    def child(self, index: int) -> "Address":
        """
        Return the address of the child at the given index.

        No assumptions are made about index continuity or bounds;
        such policies are enforced at higher layers.
        """
        if index < 0:
            raise ValueError(f"child index must be non-negative: {index}")
        return Address(self.parts + (index,))

    def is_prefix_of(self, other: "Address") -> bool:
        """
        Return True iff this address is a prefix of `other`.

        This defines the ancestor relation in address space.
        """
        return other.parts[: len(self.parts)] == self.parts

    @property
    def depth(self) -> int:
        """
        Depth of this address in the hierarchy.

        The root has depth 0.
        """
        return len(self.parts)
