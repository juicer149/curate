# curate/geometry.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Span:
    """
    Closed, inclusive interval over integer coordinates.

    Role:
        - Pure geometry: a span is just [start, end] on ℤ
        - Encodes no hierarchy, syntax, or semantics
    Invariants:
        - end >= start

    Notes:
        This type is intentionally coordinate-system agnostic.
        Whether coordinates are 0-based, 1-based, byte offsets, token indices,
        etc. is decided by producers/adapters, not by Span.
    """

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError(f"invalid span: end < start ({self.start=}, {self.end=})")

    def contains(self, other: "Span") -> bool:
        """
        Return True if `other` is fully contained within this span.

        Formal:
            [a,b] contains [c,d]  ⇔  a <= c and d <= b
        """
        return self.start <= other.start and other.end <= self.end

    def overlaps(self, other: "Span") -> bool:
        """
        Return True if this span and `other` share at least one point.

        Formal (closed intervals):
            [a,b] overlaps [c,d]  ⇔  not (b < c or d < a)
        """
        return not (self.end < other.start or other.end < self.start)

    def crosses(self, other: "Span") -> bool:
        """
        Crossing overlap: spans overlap but neither contains the other.

        Equivalent to:
            overlaps(other) and not (contains(other) or other.contains(self))
        """
        return self.overlaps(other) and not (self.contains(other) or other.contains(self))

    @property
    def length(self) -> int:
        """
        Length of the closed interval, measured in number of integer points.

        For a closed interval [start, end], the count is:
            end - start + 1

        Examples:
            Span(1, 1).length == 1
            Span(20, 30).length == 11
        """
        return self.end - self.start + 1
