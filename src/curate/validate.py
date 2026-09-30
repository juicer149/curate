# curate/validate.pyfrom __future__ import annotations

from typing import Dict, Set

from .address import Address
from .facts import ScopeSet


def validate_scope_set(scopes: ScopeSet) -> None:
    """
    Validate core invariants of a ScopeSet.

    Structural axioms enforced:

    1. Exactly one root exists at Address.root()
    2. Addresses are globally unique
    3. Parent-child relation implies full geometric containment:
           parent.span must contain child.span
    4. Spans are laminar globally:
           any two spans must be either disjoint or in a
           containment relation (no crossing overlaps)
    5. Sibling indices are contiguous per parent:
           children of a parent use indices 0..n-1 with no gaps

    Notes:
        - This validator is opt-in and intended for debugging,
          testing, and defensive validation.
        - No indexing or caching is performed.
        - O(n²) behavior is intentional and acceptable for
          validation purposes.
    """
    items = scopes.scopes
    if not items:
        raise ValueError("ScopeSet must contain at least a root")

    # ------------------------------------------------------------------
    # Root presence and uniqueness
    # ------------------------------------------------------------------
    roots = [s for s in items if s.address == Address.root()]
    if len(roots) != 1:
        raise ValueError(f"expected exactly one root, found {len(roots)}")

    # ------------------------------------------------------------------
    # Unique addresses
    # ------------------------------------------------------------------
    seen: Set[Address] = set()
    for s in items:
        if s.address in seen:
            raise ValueError(f"duplicate address detected: {s.address!r}")
        seen.add(s.address)

    # ------------------------------------------------------------------
    # Build address lookup (for parent and geometry checks)
    # ------------------------------------------------------------------
    by_addr: Dict[Address, object] = {s.address: s for s in items}  # type: ignore[dict-item]

    # ------------------------------------------------------------------
    # Geometry ↔ hierarchy consistency
    # Parent implies full geometric containment
    # ------------------------------------------------------------------
    for s in items:
        parent_addr = s.address.parent
        if parent_addr is None:
            continue

        p = by_addr.get(parent_addr)
        if p is None:
            raise ValueError(f"missing parent scope for address {s.address!r}")

        if not p.span.contains(s.span):  # type: ignore[attr-defined]
            raise ValueError(
                f"parent span does not contain child: "
                f"parent={p.span!r}, child={s.span!r}"
            )

    # ------------------------------------------------------------------
    # Global laminarity:
    # All spans must be disjoint or in containment relation
    # ------------------------------------------------------------------
    for i, a in enumerate(items):
        for j in range(i + 1, len(items)):
            b = items[j]
            sa, sb = a.span, b.span

            disjoint = sa.end < sb.start or sb.end < sa.start
            contains = sa.contains(sb) or sb.contains(sa)

            if not (disjoint or contains):
                raise ValueError(
                    f"non-laminar crossing spans: "
                    f"{a.label} {sa!r} vs {b.label} {sb!r}"
                )

    # ------------------------------------------------------------------
    # Contiguous sibling indices per parent
    # ------------------------------------------------------------------
    by_parent: Dict[Address, Set[int]] = {}
    for s in items:
        parent = s.address.parent
        if parent is None:
            continue

        idx = s.address.parts[-1]
        by_parent.setdefault(parent, set()).add(idx)

    for parent, idxs in by_parent.items():
        max_idx = max(idxs)
        expected = set(range(max_idx + 1))

        if idxs != expected:
            raise ValueError(
                f"non-contiguous children for parent {parent!r}: "
                f"have {sorted(idxs)}, expected {sorted(expected)}"
            )
