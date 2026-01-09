from __future__ import annotations

"""
Tree-sitter node interpretation.

This module applies semantic meaning to traversal:
- NodePolicy evaluation
- wrapper forwarding
- scope creation rules

It does not perform traversal itself.
"""

from typing import Optional

from ...language_rules import LanguageRules
from ...policy import NodePolicy
from .node import TSNode


def policy_for(node: TSNode, rules: LanguageRules) -> NodePolicy:
    return rules.node_policies.get(node.type, rules.default_policy)


def select_wrapper_target(node: TSNode, rules: LanguageRules) -> Optional[TSNode]:
    """
    Select the child node that receives wrapper start-line forwarding.
    """
    for rule in rules.wrapper_rules:
        if node.type != rule.wrapper_type:
            continue
        for ch in node.children:
            if ch.type in rule.target_types:
                return ch
    return None
