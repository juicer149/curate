# src/curate/engine.py
"""
Engine layer: orchestrates producers, indexing, querying and normalization.

Responsibilities:
- Connect producer → index → query → evaluator → normalize
- Provide stable, high-level API functions

Non-responsibilities:
- Tree traversal
- Language semantics
- Editor-specific behavior
"""

from __future__ import annotations

from .evaluator import ranges_for_scopes
from .index import build_index
from .normalize import normalize_ranges
from .producers import get_producer
from .query import query_from_dict, resolve_scopes
from .types import FoldMode, QueryDict, Range


def query_scopes(
    *,
    source: str,
    cursor: int,
    query: QueryDict,
    language: str = "python",
) -> tuple[Range, ...]:
    """
    Execute a structural query over source text.

    Pipeline:
    - parse source → ScopeGraph
    - index graph
    - resolve query → scopes
    - project scopes → body ranges
    - normalize ranges
    """
    producer = get_producer(language)
    graph = producer(source)
    idx = build_index(graph)

    q = query_from_dict(cursor=cursor, d=query)
    scopes = resolve_scopes(graph, idx, q)

    total_lines = len(source.splitlines()) if source else 1
    ranges = ranges_for_scopes(scopes)

    return normalize_ranges(ranges, total_lines=total_lines)


def query_ranges(
    *,
    source: str,
    cursor: int,
    query: QueryDict,
    language: str = "python",
) -> tuple[Range, ...]:
    """
    Public API: structural query → text ranges.

    Preferred entry point for:
    - AI context adapters
    - CLI tools
    - Editors
    """
    return query_scopes(
        source=source,
        cursor=cursor,
        query=query,
        language=language,
    )


# ---------------------------------------------------------------------------
# Editor convenience (NOT core API)
# ---------------------------------------------------------------------------

def fold(
    *,
    source: str,
    cursor: int,
    mode: FoldMode,
    language: str = "python",
) -> tuple[Range, ...]:
    """
    Editor convenience wrapper.

    This is NOT a core concept.
    It is a preset structural query used by editors (e.g. Neovim).
    """
    axis_map = {
        "self": "self",
        "children": "children",
        "parent": "parent",
        "ancestors": "ancestors",
        "descendants": "descendants",
    }

    return query_ranges(
        source=source,
        cursor=cursor,
        query={"axis": axis_map[mode]},
        language=language,
    )
