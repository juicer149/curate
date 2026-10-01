"""Curation: nesting follows geometry, including the outermost fact."""
from __future__ import annotations

import random

from curate import RawFact, Span
from curate.curation import curate
from curate.relations import chain
from curate.validate import validate_scope_set


def test_single_outer_fact_still_nests_its_children():
    # A file whose only top-level item is a class: the class spans exactly
    # the root. Its methods must be its children, not its siblings.
    ss = curate([
        RawFact("class", Span(1, 10)),
        RawFact("function", Span(2, 5)),
        RawFact("function", Span(6, 10)),
    ])
    assert [(s.label, s.address.parts) for s in ss.scopes] == [
        ("root", ()),
        ("class", (0,)),
        ("function", (0, 0)),
        ("function", (0, 1)),
    ]
    assert [s.label for s in chain(ss, 3)] == ["function", "class"]


def test_parent_is_always_the_innermost_containing_scope():
    rnd = random.Random(7)
    for _ in range(500):
        facts = []
        for _ in range(rnd.randint(0, 40)):
            a = rnd.randint(1, 60)
            facts.append(RawFact(rnd.choice("ABC"), Span(a, a + rnd.randint(0, 30))))
        ss = curate(facts)
        validate_scope_set(ss)
        inner = ss.scopes[1:]
        for s in inner:
            containing = [t for t in inner if t is not s and t.span.contains(s.span)]
            if containing:
                expected = min(containing, key=lambda t: t.span.length).address
            else:
                expected = ss.scopes[0].address
            assert s.address.parent == expected
