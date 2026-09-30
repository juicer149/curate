"""
curate_next.relations — algebraic relations over structural facts.

Relations are derived purely from Address algebra and ScopeSet invariants.
"""

from .core import (
    parent,
    children,
    ancestors,
    descendants,
    is_root,
    depth,
)

from .dispatch import (
    relation,
    available_relations,
    RELATIONS,
)

__all__ = [
    # core relations
    "parent",
    "children",
    "ancestors",
    "descendants",
    "is_root",
    "depth",
    # dispatch
    "relation",
    "available_relations",
    "RELATIONS",
]
