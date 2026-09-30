from __future__ import annotations

import pytest

from curate import Address
from curate.facts import Scope, ScopeSet
from curate.geometry import Span
from curate.validate import validate_scope_set


def build_scopes(scopes):
    return ScopeSet(tuple(scopes))


def test_validate_ok_on_simple_tree() -> None:
    root = Scope(Address.root(), "root", Span(10, 70))
    A = Scope(root.address.child(0), "A", Span(10, 50))
    B = Scope(A.address.child(0), "B", Span(15, 30))
    C = Scope(A.address.child(1), "C", Span(35, 45))
    D = Scope(root.address.child(1), "D", Span(60, 70))
    ss = build_scopes([root, A, B, C, D])
    validate_scope_set(ss)  # should not raise


def test_validate_detects_crossing_spans() -> None:
    root = Scope(Address.root(), "root", Span(10, 70))
    X = Scope(root.address.child(0), "X", Span(10, 40))
    Y = Scope(root.address.child(1), "Y", Span(30, 60))  # crosses X
    ss = build_scopes([root, X, Y])
    with pytest.raises(ValueError, match="non-laminar"):
        validate_scope_set(ss)


def test_validate_detects_non_contiguous_siblings() -> None:
    root = Scope(Address.root(), "root", Span(1, 100))
    c0 = Scope(root.address.child(0), "c0", Span(10, 20))
    c2 = Scope(root.address.child(2), "c2", Span(30, 40))  # gap at index 1
    ss = build_scopes([root, c0, c2])
    with pytest.raises(ValueError, match="non-contiguous"):
        validate_scope_set(ss)


def test_validate_detects_missing_parent() -> None:
    root = Scope(Address.root(), "root", Span(1, 100))
    # Child at (0,0) without its parent (0,)
    grandchild = Scope(Address.root().child(0).child(0), "gc", Span(10, 15))
    ss = build_scopes([root, grandchild])
    with pytest.raises(ValueError, match="missing parent"):
        validate_scope_set(ss)


def test_validate_detects_parent_not_containing_child() -> None:
    root = Scope(Address.root(), "root", Span(1, 100))
    parent = Scope(root.address.child(0), "P", Span(10, 20))
    child = Scope(parent.address.child(0), "C", Span(5, 15))  # not contained in P
    ss = build_scopes([root, parent, child])
    with pytest.raises(ValueError, match="parent span does not contain child"):
        validate_scope_set(ss)
