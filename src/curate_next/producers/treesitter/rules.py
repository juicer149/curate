"""treesitter.rules — data-only extraction rules

No Tree-sitter imports here.
No IO.
No runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WrapperRule:
    """
    Wrapper forwarding rule.

    Used when a syntactic wrapper should lend its start line to a child scope.

    Example (Python):
        decorated_definition wraps function_definition/class_definition
        => scope should start at decorator line
    """
    wrapper_type: str
    target_types: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LanguageRules:
    """
    Structural extraction rules for a language.

    Fields:
        scope_node_types:
            Node types that become scopes (raw Tree-sitter node.type strings).
        wrapper_rules:
            Optional wrapper forwarding rules.
    """
    scope_node_types: frozenset[str]
    wrapper_rules: tuple[WrapperRule, ...] = ()
