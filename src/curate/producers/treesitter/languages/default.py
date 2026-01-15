"""
Conservative fallback rules for unknown Tree-sitter grammars.

These rules intentionally extract only very common structural blocks
to avoid misinterpreting unfamiliar syntax trees.
"""
from __future__ import annotations

from ..rules import LanguageRules, NodePolicy

NOOP = NodePolicy(is_scope=False, noop=True)

DEFAULT_RULES = LanguageRules(
    node_policies={
        "function_definition": NodePolicy(is_scope=True, kind="function"),
        "class_definition": NodePolicy(is_scope=True, kind="class"),
        "if_statement": NodePolicy(is_scope=True, kind="if"),
        "for_statement": NodePolicy(is_scope=True, kind="for"),
        "while_statement": NodePolicy(is_scope=True, kind="while"),
        "block": NodePolicy(is_scope=True, kind="block"),
    },
    default_policy=NOOP,
)
