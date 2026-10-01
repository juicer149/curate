"""at() and chain() on the demo producer (A[10,50] > B[15,30], C[35,45]; D[60,70])."""
from __future__ import annotations

from curate import compile_scopes
from curate.relations import at, chain


def _scopes():
    return compile_scopes(source="ignored", producer="t_demo")


def labels(path) -> list[str]:
    return [s.label for s in path]


def test_at_returns_innermost_scope():
    ss = _scopes()
    assert at(ss, 20).label == "B"
    assert at(ss, 12).label == "A"
    assert at(ss, 65).label == "D"


def test_chain_runs_innermost_to_outermost_without_root():
    ss = _scopes()
    assert labels(chain(ss, 20)) == ["B", "A"]
    assert labels(chain(ss, 40)) == ["C", "A"]
    assert labels(chain(ss, 65)) == ["D"]


def test_chain_can_include_root():
    assert labels(chain(_scopes(), 20, include_root=True)) == ["B", "A", "root"]


def test_chain_is_empty_between_and_outside_scopes():
    ss = _scopes()
    assert chain(ss, 55) == ()   # inside root only
    assert chain(ss, 5) == ()    # outside everything
    assert at(ss, 5) is None
