"""curate_next.core.address — structural coordinate algebra

Address is a structural coordinate in a tree-shaped space.

Core algebra
------------
We support two safe, REPL-friendly operations:

- Extension (suffix append):
    a + 0        -> child coordinate
    a + (1, 0)   -> deeper suffix

- Cancellation (suffix removal):
    a.try_sub((1, 0)) -> Address | None   (soft / total)
    a - (1, 0)        -> Address          (strict; raises on mismatch)

This is intentionally independent of any producer or syntax tree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Tuple, overload

Suffix = Tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Address:
    """
    Immutable structural coordinate (tuple[int, ...]) with navigation helpers.
    """

    parts: Tuple[int, ...]

    # -----------------------------
    # basic protocol
    # -----------------------------

    def __iter__(self) -> Iterator[int]:
        return iter(self.parts)

    def __len__(self) -> int:
        return len(self.parts)

    def __getitem__(self, i: int | slice) -> int | Tuple[int, ...]:
        return self.parts[i]

    def to_tuple(self) -> Tuple[int, ...]:
        return self.parts

    @staticmethod
    def root() -> "Address":
        return Address((0,))

    @property
    def is_root(self) -> bool:
        return self.parts == (0,)

    @property
    def depth(self) -> int:
        return len(self.parts) - 1

    # -----------------------------
    # algebra
    # -----------------------------

    @overload
    def __add__(self, other: int) -> "Address":
        ...

    @overload
    def __add__(self, other: Suffix) -> "Address":
        ...

    def __add__(self, other: int | Suffix) -> "Address":
        if isinstance(other, int):
            return Address(self.parts + (other,))
        return Address(self.parts + tuple(other))

    def try_sub(self, suffix: Suffix) -> "Address | None":
        """
        Soft suffix cancellation.

        Returns None if the suffix does not match.
        This is what adapters and higher-level ops should usually use.
        """
        s = tuple(suffix)
        if not s:
            return self
        if len(s) > len(self.parts):
            return None
        if self.parts[-len(s) :] != s:
            return None
        return Address(self.parts[: -len(s)])

    def __sub__(self, suffix: Suffix) -> "Address":
        """
        Strict suffix cancellation (raises on mismatch).

        Useful for invariants and tests.
        """
        out = self.try_sub(suffix)
        if out is None:
            raise ValueError(
            f"suffix mismatch: {self.parts} does not end with {tuple(suffix)}"
                )
        return out

    # -----------------------------
    # convenience
    # -----------------------------

    @property
    def parent(self) -> "Address | None":
        if len(self.parts) <= 1:
            return None
        return Address(self.parts[:-1])

    def depth(self) -> int:
        return len(self.parts) - 1

    def is_prefix_of(self, other: "Address") -> bool:
        a = self.parts
        b = other.parts
        return b[: len(a)] == a
