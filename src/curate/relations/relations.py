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
