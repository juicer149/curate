from __future__ import annotations
from typing import Tuple

from ..facts import Scope, ScopeSet
from ..address import Address


def parent(scopes: ScopeSet, scope: Scope) -> Scope | None:
    if scope.address.parent is None:
        return None
    return scopes.by_address(scope.address.parent)


def children(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    out = []
    i = 0
    while True:
        child = scopes.by_address(scope.address.child(i))
        if child is None:
            break
        out.append(child)
        i += 1
    return tuple(out)


def ancestors(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    out = []
    cur = scope
    while True:
        p = parent(scopes, cur)
        if p is None:
            break
        out.append(p)
        cur = p
    return tuple(out)


def descendants(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    base = scope.address
    return tuple(
        s for s in scopes.scopes
        if base.is_prefix_of(s.address) and s.address != base
    )


def at(scopes: ScopeSet, point: int) -> Scope | None:
    """
    Return the innermost scope whose span contains `point`, or None.

    Laminarity guarantees that all containing scopes lie on one
    ancestor chain, so the deepest address is the innermost scope.
    """
    best: Scope | None = None
    for s in scopes.scopes:
        if s.span.start <= point <= s.span.end:
            if best is None or s.address.depth > best.address.depth:
                best = s
    return best


def chain(scopes: ScopeSet, point: int, *, include_root: bool = False) -> Tuple[Scope, ...]:
    """
    Return the scopes containing `point`, innermost first.

    This is the structural path from `point` outwards: the innermost
    scope, then its parent, and so on. The synthetic root is left out
    unless `include_root` is True.
    """
    inner = at(scopes, point)
    if inner is None:
        return ()
    path = (inner,) + ancestors(scopes, inner)
    if include_root:
        return path
    return tuple(s for s in path if s.address != Address.root())
