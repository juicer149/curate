"""
Tree-sitter based producer.

This package implements a concrete producer using Tree-sitter parsers
to extract structural scopes from source code.

Only build_graph is exported; all other modules are internal helpers.
"""

from __future__ import annotations

from .producer import build_graph

__all__ = ["build_graph"]
