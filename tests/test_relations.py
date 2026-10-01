from __future__ import annotations

from curate import compile_scopes
from curate.relations import parent, children, ancestors, descendants


def test_relations_on_demo() -> None:
    ss = compile_scopes(source="ignored", language="default", producer="t_demo")

    # Ensure we have expected labels
    labels = [s.label for s in ss.scopes]
    assert "root" in labels and "A" in labels and "B" in labels and "C" in labels and "D" in labels

    root = ss.scopes[0]
    cs_root = [c.label for c in children(ss, root)]
    assert cs_root == ["A", "D"]

    A = next(s for s in ss.scopes if s.label == "A")
    B = next(s for s in ss.scopes if s.label == "B")

    assert [c.label for c in children(ss, A)] == ["B", "C"]
    assert [d.label for d in descendants(ss, A)] == ["B", "C"]
    assert [a.label for a in ancestors(ss, B)] == ["A", "root"]

    # Parent utility works
    assert parent(ss, A) == root


def test_by_address_is_an_index_not_part_of_equality():
    from curate import Address, RawFact, Span
    from curate.curation import curate

    a = curate([RawFact("f", Span(1, 5)), RawFact("g", Span(2, 3))])
    b = curate([RawFact("f", Span(1, 5)), RawFact("g", Span(2, 3))])
    assert a == b
    assert a.by_address(Address((0, 0))).label == "g"
    assert a.by_address(Address((9,))) is None


def test_walking_a_large_tree_is_linear():
    # 3 000 siblings: with a scanning by_address, children() alone would be
    # ~9 million comparisons; with the index it is a few thousand lookups.
    import time

    from curate import RawFact, Span
    from curate.curation import curate
    from curate.relations import children, parent

    ss = curate([RawFact("f", Span(i * 2 + 1, i * 2 + 1)) for i in range(3000)])
    root = ss.scopes[0]
    t = time.perf_counter()
    kids = children(ss, root)
    assert all(parent(ss, k) == root for k in kids)
    assert len(kids) == 3000
    assert time.perf_counter() - t < 0.5
