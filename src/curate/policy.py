# curate/policy.py
from __future__ import annotations

from typing import Iterable

from .facts import RawFact
from .geometry import Span


# ---------------------------------------------------------------------
# Laminar selection rules
# ---------------------------------------------------------------------

def laminar_priority(fact: RawFact) -> tuple[int, int]:
    """
    Define precedence among raw facts.

    Ordering:
        - Earlier start positions take precedence
        - For equal start positions, longer spans take precedence

    This ordering ensures deterministic selection when
    conflicting observations are present.
    """
    return (fact.span.start, -fact.span.end)


def is_compatible_laminar(
    accepted: Iterable[RawFact],
    candidate: RawFact,
) -> bool:
    """
    Determine whether `candidate` is laminar-compatible with all
    previously accepted facts.

    Compatibility rules:

    Allowed:
        - Disjoint intervals
        - Proper containment (nesting)

    Forbidden:
        - Partial overlaps (crossing intervals)
        - Exact duplicate geometry (deduplicated by policy)

    Notes:
        - Identical spans are treated as conflicting observations.
          The first accepted fact wins deterministically.
        - This avoids artificial nesting chains of equal spans
          when multiple producers emit the same observation.
    """
    c = candidate.span

    for a in accepted:
        s = a.span

        # -----------------------------------------------------------------
        # Exact duplicate geometry → treat as conflict (policy choice)
        # -----------------------------------------------------------------
        if s.start == c.start and s.end == c.end:
            return False

        # -----------------------------------------------------------------
        # Disjoint (closed intervals)
        # -----------------------------------------------------------------
        if s.end < c.start or c.end < s.start:
            continue

        # -----------------------------------------------------------------
        # Containment (either direction)
        # -----------------------------------------------------------------
        if s.contains(c) or c.contains(s):
            continue

        # -----------------------------------------------------------------
        # Otherwise: crossing overlap → forbidden
        # -----------------------------------------------------------------
        return False

    return True


# ---------------------------------------------------------------------
# Root derivation rule
# ---------------------------------------------------------------------

def minimal_covering_root(facts: Iterable[RawFact]) -> Span:
    """
    Derive the minimal root span that covers all accepted facts.

    Behavior:
        - If facts are present:
            root = [min(start), max(end)]
        - If no facts are present:
            return a degenerate span [1, 1]

    This rule is coordinate-system agnostic and makes
    no assumptions about indexing conventions.
    """
    facts = tuple(facts)

    if not facts:
        return Span(1, 1)

    return Span(
        min(f.span.start for f in facts),
        max(f.span.end for f in facts),
    )
