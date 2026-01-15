"""
Tree-sitter structural rules and grammar loader for Python.
"""
from __future__ import annotations

from tree_sitter import Language
import tree_sitter_python as tspython

from ..rules import LanguageRules, NodePolicy, WrapperRule


def load_language() -> Language:
    """
    Load and return the Tree-sitter Python grammar.
    """
    return Language(tspython.language())


NOOP = NodePolicy(is_scope=False, noop=True)

PYTHON_RULES = LanguageRules(
    node_policies={
        # Definitions
        "class_definition": NodePolicy(is_scope=True, kind="class"),
        "function_definition": NodePolicy(is_scope=True, kind="function"),

        # Decorators
        "decorated_definition": NodePolicy(
            is_scope=False,
            include_in_child_start=True,
        ),

        # Control flow
        "if_statement": NodePolicy(is_scope=True, kind="if"),
        "for_statement": NodePolicy(is_scope=True, kind="for"),
        "while_statement": NodePolicy(is_scope=True, kind="while"),
        "with_statement": NodePolicy(is_scope=True, kind="with"),
        "try_statement": NodePolicy(is_scope=True, kind="try"),
        "match_statement": NodePolicy(is_scope=True, kind="match"),

        # Clauses
        "elif_clause": NodePolicy(is_scope=True, kind="elif"),
        "else_clause": NodePolicy(is_scope=True, kind="else"),
        "except_clause": NodePolicy(is_scope=True, kind="except"),
        "finally_clause": NodePolicy(is_scope=True, kind="finally"),
        "case_clause": NodePolicy(is_scope=True, kind="case"),
    },
    default_policy=NOOP,
    wrapper_rules=(
        WrapperRule(
            wrapper_type="decorated_definition",
            target_types=("class_definition", "function_definition"),
        ),
    ),
)
