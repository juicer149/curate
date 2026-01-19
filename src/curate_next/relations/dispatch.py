"""curate.relations.dispatch — string-based adapter over relations.core.

This module provides a small, orthogonal dispatch surface:

    relation(scopes, scope, name)

It is intended for UI/CLI/LSP/config driven use-cases where a relation is
selected dynamically (e.g. from user input).

Non-goals:
- no new semantics
- no interpretation
- no query language beyond selecting a named relation
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


# Registry of supported relations.
# Keep this small and stable: it defines the string API surface.
# skulle jag kunna göra detta till json eller ska jag ha kvar detta som kod?
RELATIONS: Mapping[str, RelationSpec] = {
    "parent": RelationSpec("parent", core.parent, 2, "Immediate parent scope (or None)."),
    "children": RelationSpec("children", core.children, 2, "Direct child scopes."),
    "siblings": RelationSpec("siblings", core.siblings, 2, "Sibling scopes (same parent)."),
    "ancestors": RelationSpec("ancestors", core.ancestors, 2, "All ancestors (nearest first)."),
    "descendants": RelationSpec("descendants", core.descendants, 2, "All descendants (deterministic)."),
    "is_root": RelationSpec("is_root", core.is_root, 1, "True if scope is root."),
    "depth": RelationSpec("depth", core.depth, 1, "Structural depth (root == 0)."),
}


def relation(scopes: ScopeSet, scope: Scope, name: str) -> Any:
    """
    Dispatch a named relation over `scope` within `scopes`.

    Args:
        scopes: ScopeSet to operate within.
        scope: The target scope.
        name: Relation name (e.g. "parent", "ancestors", "depth").

    Returns:
        The result of the selected relation function.

    Raises:
        ValueError: If name is unknown.
        RuntimeError: If a registry entry is malformed.
    """
    spec = RELATIONS.get(name)
    if spec is None:
        available = ", ".join(sorted(RELATIONS))
        raise ValueError(f"Unknown relation: {name!r}. Available: {available}")

    if spec.arity == 2:
        return spec.fn(scopes, scope)
    if spec.arity == 1:
        return spec.fn(scope)

    # Defensive: should never happen if Arity is respected.
    raise RuntimeError(f"Invalid arity for relation: {name!r} ({spec.arity!r})")


def available_relations() -> tuple[str, ...]:
    """Return supported relation names (stable ordering)."""
    return tuple(sorted(RELATIONS))
