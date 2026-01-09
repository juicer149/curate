from __future__ import annotations

"""
LanguageRules = all language-specific semantics as data.

Traversal code must not branch on language names.
"""

from dataclasses import dataclass

from .policy import NodePolicy
from .wrapper import WrapperRule


@dataclass(frozen=True, slots=True)
class LanguageRules:
    """
    Configuration for a language backend.

    node_policies:
      Mapping from node.type -> NodePolicy

    default_policy:
      Policy for unknown node types (typically NOOP)

    wrapper_rules:
      Declarative rules for wrapper forwarding
    """

    node_policies: dict[str, NodePolicy]
    default_policy: NodePolicy
    wrapper_rules: tuple[WrapperRule, ...] = ()
