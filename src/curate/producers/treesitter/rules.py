"""
Tree-sitter structural rule definitions.

This module defines *data-only* descriptions of how syntax tree nodes
map to Curate scopes.

Rules must not:
- import Tree-sitter
- load grammars
- perform I/O

They are pure structural semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class NodePolicy:
    """
    Policy describing how a Tree-sitter node participates in scope construction.

    is_scope:
        Whether this node creates a new Scope.

    noop:
        If True, this node is transparent and recursion continues through it.

    include_in_child_start:
        Used for wrapper nodes (e.g. decorators). The wrapper's start line
        is forwarded into a selected child scope.

    kind:
        Optional override for the scope kind label.
    """
    is_scope: bool
    noop: bool = False
    include_in_child_start: bool = False
    kind: Optional[str] = None


@dataclass(frozen=True, slots=True)
class WrapperRule:
    """
    Describes a wrapper node that forwards its start position
    into one of its children.

    Example:
        decorated_definition → function_definition
    """
    wrapper_type: str
    target_types: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LanguageRules:
    """
    Complete structural ruleset for a Tree-sitter grammar.

    node_policies:
        Mapping from node.type → NodePolicy.

    default_policy:
        Policy applied to nodes not explicitly listed.

    wrapper_rules:
        Optional rules for wrapper nodes.
    """
    node_policies: dict[str, NodePolicy]
    default_policy: NodePolicy
    wrapper_rules: tuple[WrapperRule, ...] = ()
