"""
Tests for context-manager usage patterns.

These tests verify properties critical for building AI context managers:
- Multiple queries are independent and stable
- ScopeGraph is truly immutable
- Structural facts are deterministic across queries
- Ranges are always valid for text slicing
"""

from pathlib import Path

from curate import query_ranges
from curate.engine import query_scopes
from curate.producers import get_producer
from curate.index import build_index

FIXTURE = Path(__file__).parent / "fixtures/python_minimal.py"
TEXT = FIXTURE.read_text(encoding="utf-8")


def test_multiple_queries_are_independent():
    """
    Invariant: Multiple queries on the same source must be independent.
    
    A context manager will run many queries on the same file.
    No query should affect any other query's results.
    """
    # Same source, different cursors, different queries
    r1 = query_ranges(source=TEXT, cursor=7, query={"axis": "self"}, language="python")
    r2 = query_ranges(source=TEXT, cursor=12, query={"axis": "children"}, language="python")
    r3 = query_ranges(source=TEXT, cursor=7, query={"axis": "self"}, language="python")
    
    # First and third query are identical - must return same result
    assert r1 == r3
    
    # Second query is different - should not affect others
    assert isinstance(r2, tuple)


def test_scope_graph_is_truly_immutable():
    """
    Invariant: ScopeGraph never changes after creation.
    
    Context managers will reuse the same graph for multiple queries.
    The graph must be completely immutable.
    """
    producer = get_producer("python")
    graph1 = producer(TEXT)
    
    # Create index and run queries
    idx = build_index(graph1)
    from curate.query import query_from_dict, resolve_scopes
    
    q1 = query_from_dict(cursor=7, d={"axis": "self"})
    scopes1 = resolve_scopes(graph1, idx, q1)
    
    # Re-produce graph - should be identical
    graph2 = producer(TEXT)
    assert graph1.scopes == graph2.scopes
    
    # Original graph should be unchanged
    q2 = query_from_dict(cursor=12, d={"axis": "children"})
    scopes2 = resolve_scopes(graph1, idx, q2)
    
    # Verify original graph still produces same results
    scopes1_again = resolve_scopes(graph1, idx, q1)
    assert scopes1 == scopes1_again


def test_ranges_are_valid_for_text_slicing():
    """
    Invariant: All returned ranges must be valid for slicing source text.
    
    Context managers need to extract actual text using these ranges.
    Every range must be safe to use with splitlines()[start-1:end].
    """
    lines = TEXT.splitlines()
    
    for cursor in range(1, len(lines) + 1):
        for axis in ("self", "children", "parent", "ancestors"):
            ranges = query_ranges(
                source=TEXT,
                cursor=cursor,
                query={"axis": axis},
                language="python",
            )
            
            for start, end in ranges:
                # Must be valid indices
                assert 1 <= start <= end <= len(lines)
                
                # Must be safe to slice (0-indexed slicing)
                text_slice = lines[start - 1:end]
                assert isinstance(text_slice, list)
                assert len(text_slice) == end - start + 1


def test_header_body_separation_is_consistent():
    """
    Invariant: Headers and bodies never overlap.
    
    Context managers may want to show only headers (skeleton view)
    or only bodies (detail view). These must be disjoint.
    """
    producer = get_producer("python")
    graph = producer(TEXT)
    
    for scope in graph.scopes:
        header = scope.header_range()
        body = scope.body_range()
        
        # Header must be valid
        assert header[0] <= header[1]
        assert header[0] == scope.start
        
        if body is not None:
            # Body must be valid
            assert body[0] <= body[1]
            assert body[1] == scope.end
            
            # Header and body must not overlap
            assert header[1] < body[0]


def test_scope_kinds_are_stable():
    """
    Invariant: Scope kinds are deterministic for the same input.
    
    Context managers may filter by kind (all functions, all classes).
    Kind labels must be stable across runs.
    """
    producer = get_producer("python")
    
    graph1 = producer(TEXT)
    kinds1 = {s.kind for s in graph1.scopes}
    
    graph2 = producer(TEXT)
    kinds2 = {s.kind for s in graph2.scopes}
    
    assert kinds1 == kinds2
    
    # Python fixture should have expected kinds
    assert "module" in kinds1
    assert "function" in kinds1


def test_laminar_property_strict():
    """
    Invariant: ScopeGraph is laminar (nested or disjoint, never partial overlap).
    
    This is CRITICAL for context managers - they rely on clean hierarchies.
    """
    producer = get_producer("python")
    graph = producer(TEXT)
    
    scopes = list(graph.scopes)
    
    for i, s1 in enumerate(scopes):
        for s2 in scopes[i + 1:]:
            # Either nested or disjoint
            s1_range = set(range(s1.start, s1.end + 1))
            s2_range = set(range(s2.start, s2.end + 1))
            
            intersection = s1_range & s2_range
            
            if intersection:
                # If they intersect, one must contain the other
                assert s1_range <= s2_range or s2_range <= s1_range, \
                    f"Partial overlap detected: {s1} vs {s2}"


def test_empty_source_is_safe():
    """
    Invariant: Empty source must not crash and must return valid graph.
    
    Context managers may encounter empty files.
    """
    producer = get_producer("python")
    graph = producer("")
    
    assert len(graph.scopes) >= 1  # At least module scope
    assert graph.scopes[0].kind == "module"
    assert graph.scopes[0].start == 1
    assert graph.scopes[0].end == 1


def test_single_line_source_is_safe():
    """
    Invariant: Single-line source must produce valid graph.
    
    Context managers need to handle minimal files.
    """
    source = "x = 1"
    producer = get_producer("python")
    graph = producer(source)
    
    assert len(graph.scopes) >= 1
    assert graph.scopes[0].start == 1
    assert graph.scopes[0].end == 1


def test_query_with_kind_filter():
    """
    Invariant: Kind filtering must be accurate and stable.
    
    Context managers will use this to extract "all functions" etc.
    """
    from curate.query import query_from_dict, resolve_scopes
    
    producer = get_producer("python")
    graph = producer(TEXT)
    idx = build_index(graph)
    
    # Get all functions
    q = query_from_dict(
        cursor=1,
        d={"axis": "descendants", "kinds": ["function"]}
    )
    scopes = resolve_scopes(graph, idx, q)
    
    # All returned scopes must be functions
    for scope in scopes:
        assert scope.kind == "function"
    
    # Python fixture has 3 functions: top, inner, m
    assert len(scopes) == 3


def test_max_items_limit_is_respected():
    """
    Invariant: max_items limit must be strictly enforced.
    
    Context managers need this for token budget control.
    """
    from curate.query import query_from_dict, resolve_scopes
    
    producer = get_producer("python")
    graph = producer(TEXT)
    idx = build_index(graph)
    
    # Limit to 2 items
    q = query_from_dict(
        cursor=1,
        d={"axis": "descendants", "max_items": 2}
    )
    scopes = resolve_scopes(graph, idx, q)
    
    assert len(scopes) <= 2


def test_parallel_query_execution_safe():
    """
    Invariant: Multiple threads could query the same graph safely.
    
    Context managers may parallelize queries.
    (This test just ensures no mutable state is shared)
    """
    queries = [
        {"axis": "self"},
        {"axis": "children"},
        {"axis": "descendants"},
        {"axis": "ancestors"},
    ]
    
    results = []
    for q in queries:
        r = query_ranges(source=TEXT, cursor=7, query=q, language="python")
        results.append(r)
    
    # All should succeed without interference
    assert all(isinstance(r, tuple) for r in results)
    
    # Running same query again should give same result
    r1 = query_ranges(source=TEXT, cursor=7, query={"axis": "self"}, language="python")
    assert r1 == results[0]


def test_source_with_only_newlines():
    """
    Invariant: Source with only whitespace must not crash.
    
    Edge case for context managers.
    """
    source = "\n\n\n\n"
    producer = get_producer("python")
    graph = producer(source)
    
    assert len(graph.scopes) >= 1
    assert graph.scopes[0].kind == "module"


def test_deeply_nested_structure():
    """
    Invariant: Deep nesting must not cause stack overflow or corruption.
    
    Context managers may encounter deeply nested code.
    """
    # Create deeply nested if statements
    depth = 20
    indent = ""
    lines = []
    for i in range(depth):
        lines.append(f"{indent}if True:")
        indent += "    "
    lines.append(f"{indent}pass")
    
    source = "\n".join(lines)
    producer = get_producer("python")
    graph = producer(source)
    
    # Should produce valid graph
    assert len(graph.scopes) >= depth
    
    # All scopes should be properly nested
    for scope in graph.scopes:
        assert scope.start <= scope.end
