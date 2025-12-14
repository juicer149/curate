from dataclasses import dataclass
from typing import Optional, Tuple
from .line import Line


@dataclass(frozen=True)
class Entity:
    """
    A semantic entity.

    An entity is either:
    - code   (class, function)
    - docs   (docstring)

    It owns a head and an optional body.
    """
    is_code: bool
    kind: Optional[str]          # "class", "function", "docstring"
    name: Optional[str]
    head: Tuple[Line, ...]
    body: Tuple[Line, ...]

    @property
    def all_lines(self) -> Tuple[Line, ...]:
        return self.head + self.body

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "name": self.name,
            "is_code": self.is_code,
            "head": [l.number for l in self.head],
            "body": [l.number for l in self.body],
        }
