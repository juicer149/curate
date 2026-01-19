"""
curate.relations — algebraic relations over structural facts.

This package exposes structural relations derived purely from Scope.address.

It provides:
- core: explicit typed relation functions
- dispatch: optional string-based adapter for dynamic selection (UI/CLI/LSP)

Relations are:
- deterministic
- interpretation-free
- independent of syntax trees, languages, and files

No indexes are required for correctness.
"""

from .core import (
    parent,
    children,
    siblings,
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
    # core
    "parent",
    "children",
    "siblings",
    "ancestors",
    "descendants",
    "is_root",
    "depth",
    # dispatch adapter
    "relation",
    "available_relations",
    "RELATIONS",
]
