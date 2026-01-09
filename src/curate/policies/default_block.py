from __future__ import annotations

"""
Conservative fallback rules for unknown languages.
"""

from ..policy import NodePolicy
from ..language_rules import LanguageRules

NOOP = NodePolicy(is_scope=False, noop=True)

DEFAULT_BLOCK_RULES = LanguageRules(
    node_policies={
        "block": NodePolicy(is_scope=True, kind="block"),
        "function_definition": NodePolicy(is_scope=True, kind="function"),
        "class_definition": NodePolicy(is_scope=True, kind="class"),
        "if_statement": NodePolicy(is_scope=True, kind="if"),
        "for_statement": NodePolicy(is_scope=True, kind="for"),
        "while_statement": NodePolicy(is_scope=True, kind="while"),
    },
    default_policy=NOOP,
)
