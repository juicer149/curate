# curate/curation.py
from __future__ import annotations

from typing import Iterable, Dict, List

from .facts import RawFact, Scope, ScopeSet
from .address import Address
from . import policy


# ---------------------------------------------------------------------
# Laminar selection (policy-driven, allows nesting)
# ---------------------------------------------------------------------

def select_laminar(facts: Iterable[RawFact]) -> list[RawFact]:
    """
    Select a laminar subset of raw facts, allowing nesting
    (containment) but disallowing crossing overlaps.

    Properties:
        - Deterministic
        - Total
        - Allows hierarchical structure to emerge
        - O(n log n): one sort, then a single pass

    Algorithm:
        Facts are visited in policy order (start ascending, longer first).
        A stack holds the accepted facts that are still "open", i.e. whose
        span may contain later facts. Before a candidate is checked, every
        open fact that ends before the candidate starts is closed (popped):
        it is disjoint from this and every later candidate.

        What remains on top is the innermost accepted fact that overlaps
        the candidate. Deeper stack entries contain the top, so checking
        the candidate against the top alone is equivalent to checking it
        against every accepted fact. The rule itself stays in `policy`.
    """
    ordered = sorted(facts, key=policy.laminar_priority)

    accepted: list[RawFact] = []
    open_stack: list[RawFact] = []

    for fact in ordered:
        while open_stack and open_stack[-1].span.end < fact.span.start:
            open_stack.pop()

        if policy.is_compatible_laminar(open_stack[-1:], fact):
            accepted.append(fact)
            open_stack.append(fact)

    return accepted


# ---------------------------------------------------------------------
# Address assignment
# ---------------------------------------------------------------------

def assign_addresses(facts: list[RawFact]) -> ScopeSet:
    """
    Assign hierarchical addresses to a laminar sequence of facts.

    Precondition:
        `facts` is laminar and in policy order (as returned by
        `select_laminar`).

    Strategy:
        - Inject a single root scope
        - The parent is the innermost open scope that contains the fact
          (a containment stack, O(n) overall)
        - Assign child indices contiguously per parent
    """
    scopes: List[Scope] = []
    next_index: Dict[Address, int] = {}

    root = Scope(
        address=Address.root(),
        label="root",
        span=policy.minimal_covering_root(facts),
    )

    scopes.append(root)
    next_index[root.address] = 0

    open_stack: List[Scope] = []

    for fact in facts:
        while open_stack and not open_stack[-1].span.contains(fact.span):
            open_stack.pop()

        parent = open_stack[-1] if open_stack else root

        idx = next_index[parent.address]
        next_index[parent.address] = idx + 1

        addr = parent.address.child(idx)

        scope = Scope(
            address=addr,
            label=fact.label,
            span=fact.span,
        )

        scopes.append(scope)
        next_index[addr] = 0
        open_stack.append(scope)

    return ScopeSet(tuple(scopes))


# ---------------------------------------------------------------------
# Public curation entrypoint
# ---------------------------------------------------------------------

def curate(facts: Iterable[RawFact]) -> ScopeSet:
    """
    Curate raw facts into a ScopeSet.

    This function is the sole owner of structural policy
    in Curate.
    """
    laminar = select_laminar(facts)
    return assign_addresses(laminar)
