from dataclasses import dataclass
from typing import Tuple
from .entity import Entity
from .line import Line


@dataclass
class Scope:
    """
    A lexical scope.

    A scope owns:
    - lines: all lines belonging to this scope
    - entities: entities declared directly in this scope
    - children: nested scopes
    """
    lines: Tuple[Line, ...]
    entities: Tuple[Entity, ...] = ()
    children: Tuple["Scope", ...] = ()

    def add_entity(self, entity: Entity) -> None:
        self.entities += (entity,)

    def add_child(self, scope: "Scope") -> None:
        self.children += (scope,)
