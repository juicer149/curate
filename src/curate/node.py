"""
Structural node model.

Place in pipeline:
- Used internally by backends to represent ownership
  of contiguous line spans.

The engine never depends on Node.
Adapters never see Node.

This model exists solely to support structure extraction
inside backend implementations.
"""

from dataclasses import dataclass, field
from typing import Optional, Iterator


@dataclass(slots=True)
class Node:
    kind: str
    start: int
    end: int
    parent: Optional["Node"] = None
    children: list["Node"] = field(default_factory=list)

    def __iter__(self) -> Iterator["Node"]:
        return iter(self.children)

    def contains(self, line: int) -> bool:
        return self.start <= line <= self.end

    @property
    def width(self) -> int:
        return self.end - self.start

    @property
    def orphan(self) -> bool:  # pragma: no cover
        return self.parent is None

    @property
    def has_children(self) -> bool:  # pragma: no cover
        return bool(self.children)
