from __future__ import annotations

import pytest

from curate.geometry import Span


def test_span_invariants_closed_interval() -> None:
    with pytest.raises(ValueError):
        Span(5, 4)  # end < start

    assert Span(5, 5).length == 1
    assert Span(5, 7).length == 3


def test_contains_and_overlaps_boundaries() -> None:
    a = Span(10, 20)
    b = Span(12, 15)
    c = Span(21, 30)
    d = Span(20, 25)  # shares endpoint with a

    assert a.contains(b)
    assert not b.contains(a)

    # Closed intervals: touching at boundary does not overlap unless shared point exists
    assert not a.overlaps(c)  # [10,20] vs [21,30] => no overlap
    assert a.overlaps(d)      # [10,20] vs [20,25] share point 20


def test_crosses_definition() -> None:
    a = Span(10, 20)
    b = Span(15, 25)  # overlaps a but neither contains the other
    c = Span(5, 30)   # contains a
    d = Span(21, 22)  # disjoint

    assert a.crosses(b)
    assert not a.crosses(c)
    assert not a.crosses(d)
    # identical geometry does not “cross”
    assert not a.crosses(Span(10, 20))
