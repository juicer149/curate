"""curate_next.relations.dispatch — string-based adapter over relations.core

This module provides a minimal dispatch surface for dynamic use-cases
(UI, CLI, LSP, config-driven systems).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Any, Literal

from ..facts import Scope, ScopeSet
from . import core


Arity = Literal[1, 2]


@dataclass(frozen=True, slots=True)
class RelationSpec:
    """A named relation callable exposed via dispatch."""
    name: str
    fn: Callable[..., Any]
    arity: Arity
    doc: str = ""


# Stable, explicit string API.
RELATIONS: Mapping[str, RelationSpec] = {
    "parent": RelationSpec(
        "parent", core.parent, 2, "Immediate parent scope (or None)."
    ),
    "children": RelationSpec(
        "children", core.children, 2, "Direct child scopes."
    ),
    "ancestors": RelationSpec(
        "ancestors", core.ancestors, 2, "All ancestors (nearest first)."
    ),
    "descendants": RelationSpec(
        "descendants", core.descendants, 2, "All descendants."
    ),
    "is_root": RelationSpec(
        "is_root", core.is_root, 1, "True if scope is root."
    ),
    "depth": RelationSpec(
        "depth", core.depth, 1, "Structural depth (root == 0)."
    ),
}


def relation(scopes: ScopeSet, scope: Scope, name: str) -> Any:
    """
    Dispatch a named relation over `scope` within `scopes`.
    """
    spec = RELATIONS.get(name)
    if spec is None:
        available = ", ".join(sorted(RELATIONS))
        raise ValueError(f"Unknown relation: {name!r}. Available: {available}")

    if spec.arity == 2:
        return spec.fn(scopes, scope)
    if spec.arity == 1:
        return spec.fn(scope)

    # Defensive: should never happen.
    raise RuntimeError(f"Invalid arity for relation: {name!r}")


def available_relations() -> tuple[str, ...]:
    """Return supported relation names (stable ordering)."""
    return tuple(sorted(RELATIONS))
