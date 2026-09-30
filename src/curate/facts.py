from __future__ import annotations

"""
Core data model for Curate.

This module defines the fundamental data types used to represent
structural information at different stages of the pipeline:

    - RawFact / RawFactSet:
        Uncurated, producer-emitted observations about structure.
        These represent claims, not truth, and may be inconsistent,
        overlapping, or incomplete.

    - Scope / ScopeSet:
        Curated, internally consistent structural results produced
        by the curation process. These represent accepted structure
        and form the canonical model consumed by downstream systems.

The distinction between raw facts and scopes is fundamental:
    producers observe,
    curation decides,
    scopes represent structure.
"""

from dataclasses import dataclass
from typing import Iterable, Tuple

from .geometry import Span
from .address import Address


# ---------------------------------------------------------------------
# Producer-emitted observations
# ---------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class RawFact:
    """
    Producer-emitted structural observation.

    A RawFact represents a claim about structure over a span,
    not an accepted truth. Raw facts may overlap, contradict
    each other, or be incomplete.

    Role:
        - Observe a labeled span
        - Carry no hierarchy or structural commitment

    Invariants:
        - Span is valid geometry
        - No address or hierarchy is attached
    """

    label: str
    span: Span


@dataclass(frozen=True, slots=True)
class RawFactSet:
    """
    Immutable collection of RawFact.

    RawFactSet represents unordered observational input.
    It carries no guarantees about consistency, laminarity,
    or completeness.

    Properties:
        - Facts may overlap
        - Facts may contradict
        - Facts may be incomplete or empty

    This type is strictly an input container; no structure
    or policy is implied.
    """

    items: Tuple[RawFact, ...]

    @classmethod
    def from_iter(cls, it: Iterable[RawFact]) -> "RawFactSet":
        """
        Construct a RawFactSet from an iterable of RawFact.
        """
        return cls(tuple(it))


# ---------------------------------------------------------------------
# Curated structural results
# ---------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Scope:
    """
    Curated structural unit.

    A Scope represents accepted structure after curation.
    Hierarchy is defined solely by its Address; geometry
    is defined by its Span.

    Scopes are derived artifacts and are never emitted
    directly by producers.

    Role:
        - Represent accepted structural units
        - Bind geometry (Span) to structure (Address)

    Invariants:
        - Address is unique within a ScopeSet
        - Spans are laminar across the containing ScopeSet
    """

    address: Address
    label: str
    span: Span


@dataclass(frozen=True, slots=True)
class ScopeSet:
    """
    Immutable set of curated scopes.

    ScopeSet is the canonical structural result of curation.
    All hierarchical relations are derived from addresses;
    no parent/child pointers or indexes are stored.

    Role:
        - Represent final, internally consistent structure
        - Serve as the sole source of structural truth

    Invariants:
        - Exactly one root scope exists
        - Addresses are unique
        - For each parent address, child addresses use
          contiguous integer indices starting at 0

    Critical note:
        Several derived relations (e.g. ``children``) rely
        on the contiguity of sibling indices for correctness
        and termination. Violating this invariant results in
        undefined behavior for relation helpers.

    Notes:
        This type intentionally avoids indexing or caching.
        Consumers requiring faster lookup are expected to
        build derived indexes externally, while preserving
        these invariants.
    """

    scopes: Tuple[Scope, ...]

    def by_address(self, addr: Address) -> Scope | None:
        """
        Return the Scope with the given address, if present.

        This is a linear scan by design. Indexing and caching
        are expected to be handled outside the core model.
        """
        for s in self.scopes:
            if s.address == addr:
                return s
        return None
