from __future__ import annotations

from curate.facts import RawFact
from curate.geometry import Span
from curate import policy


def test_is_compatible_laminar_rules() -> None:
    accepted = [
        RawFact("A", Span(10, 50)),
        RawFact("B", Span(15, 30)),  # nested in A
    ]

    # Disjoint allowed
    assert policy.is_compatible_laminar(accepted, RawFact("D", Span(60, 70)))

    # Containment allowed
    assert policy.is_compatible_laminar(accepted, RawFact("C", Span(35, 45)))

    # Crossing forbidden
    assert not policy.is_compatible_laminar(accepted, RawFact("X", Span(25, 60)))

    # Exact duplicate geometry forbidden (policy dedup)
    assert not policy.is_compatible_laminar(accepted, RawFact("A_DUP", Span(10, 50)))
