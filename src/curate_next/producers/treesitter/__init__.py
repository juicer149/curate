"""
Tree-sitter producer backend.

Exports:
- build_scope_set(source, language) -> ScopeSet
"""

from .producer import build_scope_set

__all__ = ["build_scope_set"]
