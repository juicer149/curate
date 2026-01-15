# src/curate/__init__.py
"""
curate public API surface.

This module deliberately exposes only a *very small* set of entry points.
The intention is that most consumers interact with curate as a black box
query engine rather than importing internal modules.

Exposed functions:
- fold:        convenience wrapper for folding-like relations
- query_scopes: general structural query interface
- query_ranges: alias of query_scopes for naming clarity

Everything else in the package is considered internal and unstable.
"""

from __future__ import annotations

from .engine import fold, query_ranges, query_scopes

__all__ = ["fold", "query_ranges", "query_scopes"]
