# src/curate/tests/benchmark_validate.py
from __future__ import annotations

import pytest

from curate import Address
from curate.facts import Scope, ScopeSet
from curate.geometry import Span
from curate.validate import validate_scope_set


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def build_deep_chain(n: int) -> ScopeSet:
    """
    Deep strictly nested chain:

    root
      └─ A0
          └─ A1
              └─ ...

    Strict containment at every step.
    """
    scopes: list[Scope] = []

    root = Scope(Address.root(), "root", Span(0, n * 100))
    scopes.append(root)

    parent = root
    for i in range(n):
        start = parent.span.start + 1
        end = parent.span.end - 1
        child = Scope(parent.address.child(0), f"A{i}", Span(start, end))
        scopes.append(child)
        parent = child

    return ScopeSet(tuple(scopes))


def build_wide_root(n: int) -> ScopeSet:
    """
    Wide tree:

    root
      ├─ A0
      ├─ A1
      └─ ...

    Children disjoint and strictly contained in root.
    """
    scopes: list[Scope] = []

    root = Scope(Address.root(), "root", Span(0, n * 10))
    scopes.append(root)

    for i in range(n):
        start = i * 10 + 1
        end = start + 5
        child = Scope(root.address.child(i), f"A{i}", Span(start, end))
        scopes.append(child)

    return ScopeSet(tuple(scopes))


def build_balanced_tree(depth: int, fanout: int) -> ScopeSet:
    """
    Balanced laminar tree.

    Properties guaranteed:
    - Every child span is STRICTLY contained in its parent span
    - Siblings are disjoint
    - Addresses are contiguous per parent (0..fanout-1)
    - Works for any depth>=1, fanout>=2 given enough space

    Implementation strategy:
    - Each node's usable interior is (start+1 .. end-1)
    - Split that interior into fanout disjoint segments
    - Recurse using each child span as the new parent span
    """
    if depth < 1:
        raise ValueError("depth must be >= 1")
    if fanout < 2:
        raise ValueError("fanout must be >= 2")

    # Ensure enough geometric "room" for strict containment through depth.
    # Each level consumes at least 2 points for strict nesting (one on each side),
    # and we need some width to split among fanout children.
    #
    # A simple safe size: grow exponentially with depth/fanout.
    base = (fanout ** (depth + 2)) * 4
    root = Scope(Address.root(), "root", Span(0, base))

    scopes: list[Scope] = [root]

    def rec(parent: Scope, level: int) -> None:
        if level == 0:
            return

        inner_start = parent.span.start + 1
        inner_end = parent.span.end - 1
        inner_width = inner_end - inner_start + 1

        # Need at least fanout points to give each child a non-empty segment.
        # Also, to allow further strict containment, children should have at least width 3
        # (so their own inner zone isn't empty), but we keep this minimal and deterministic.
        if inner_width < fanout:
            raise ValueError(
                f"insufficient span width for fanout={fanout} at level={level}: "
                f"parent={parent.span!r}"
            )

        # Partition inner_width into fanout disjoint chunks deterministically.
        q, r = divmod(inner_width, fanout)  # base chunk size, remainder
        cursor = inner_start

        for i in range(fanout):
            chunk = q + (1 if i < r else 0)
            child_start = cursor
            child_end = cursor + chunk - 1
            cursor = child_end + 1

            child = Scope(
                parent.address.child(i),
                f"L{level}_{i}",
                Span(child_start, child_end),
            )
            scopes.append(child)
            rec(child, level - 1)

    rec(root, depth)
    return ScopeSet(tuple(scopes))


# ---------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------

@pytest.mark.benchmark(group="validate/deep")
def test_validate_deep_chain(benchmark):
    ss = build_deep_chain(200)
    benchmark(validate_scope_set, ss)


@pytest.mark.benchmark(group="validate/wide")
def test_validate_wide_root(benchmark):
    ss = build_wide_root(500)
    benchmark(validate_scope_set, ss)


@pytest.mark.benchmark(group="validate/balanced")
def test_validate_balanced_tree(benchmark):
    ss = build_balanced_tree(depth=4, fanout=5)
    benchmark(validate_scope_set, ss)
