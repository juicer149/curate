"""
Curate — semantic code structure analyzer.

Public API surface for editor and tooling integrations.
"""

# -------------------------------------------------
# High-level analysis (entry points)
# -------------------------------------------------

from .api import analyze_file, analyze_text

# -------------------------------------------------
# Engine (editor-facing, stable API)
# -------------------------------------------------

from .engine import fold_for_cursor, Action

# -------------------------------------------------
# Query layer (advanced / power users)
# -------------------------------------------------

from .query import (
    entities_at_line,
    best_entity_at_line,
    scope_at_line,
    parent_entity,
    direct_children,
    descendants,
)

# -------------------------------------------------
# Views & folding (low-level building blocks)
# -------------------------------------------------

from .views import ViewMode, view_lines
from .foldplan import fold_plan_for_view

# -------------------------------------------------
# Public API contract
# -------------------------------------------------

__all__ = [
    # analysis
    "analyze_file",
    "analyze_text",

    # engine
    "fold_for_cursor",
    "Action",

    # queries
    "entities_at_line",
    "best_entity_at_line",
    "scope_at_line",
    "parent_entity",
    "direct_children",
    "descendants",

    # views / folding
    "ViewMode",
    "view_lines",
    "fold_plan_for_view",
]
