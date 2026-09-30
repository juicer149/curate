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
        - Allows hierarchical structure to emerge    """
    ordered = sorted(facts, key=policy.laminar_priority)

    accepted: list[RawFact] = []

    for fact in ordered:
        if policy.is_compatible_laminar(accepted, fact):
            accepted.append(fact)

    return accepted


# ---------------------------------------------------------------------
# Address assignment
# ---------------------------------------------------------------------

def assign_addresses(facts: list[RawFact]) -> ScopeSet:
    """
    Assign hierarchical addresses to a laminar sequence of facts.

    Strategy:
        - Inject a single root scope
        - Choose the parent as the deepest containing scope
        - Assign child indices contiguously per parent
    """
    scopes: list[Scope] = []
    next_index: Dict[Address, int] = {}

    root = Scope(
        address=Address.root(),
        label="root",
        span=policy.minimal_covering_root(facts),
    )

    scopes.append(root)
    next_index[root.address] = 0

    for fact in facts:
        parent = root

        for s in scopes:
            if s.span.contains(fact.span) and s.span.length < parent.span.length:
                parent = s

        idx = next_index.get(parent.address, 0)
        next_index[parent.address] = idx + 1

        addr = parent.address.child(idx)

        scope = Scope(
            address=addr,
            label=fact.label,
            span=fact.span,
        )

        scopes.append(scope)
        next_index[addr] = 0

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
