"""
Curate — structural facts engine.

Public surface:
- compile_scope_set / compile_scope_sets
- build_index / scope_at_line
- relations
- query_ranges / fold
"""

from .facts import Scope, ScopeSet
from .compile import SourceUnit, compile_scope_set, compile_scope_sets
from .index import Index, build_index, scope_at_line
from . import relations
from .query import Query, query_ranges, fold

__all__ = [
    "Scope",
    "ScopeSet",
    "SourceUnit",
    "compile_scope_set",
    "compile_scope_sets",
    "Index",
    "build_index",
    "scope_at_line",
    "relations",
    "Query",
    "query_ranges",
    "fold",
]
