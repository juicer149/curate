"""
curate.relations — algebraic relations over structural facts.

This package exposes structural relations derived purely
from Scope.id (hierarchical structural addresses).

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

__all__ = [
    "parent",
    "children",
    "siblings",
    "ancestors",
    "descendants",
    "is_root",
    "depth",
]
