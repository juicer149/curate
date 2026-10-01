"""Python: definitions and compound statements."""

from __future__ import annotations

from typing import Any

from ..spec import LanguageSpec

NAMES = ("python", "py")
EXTENSIONS = (".py", ".pyi")


def _load() -> Any:
    import tree_sitter_python as ts
    from tree_sitter import Language

    return Language(ts.language())


SPEC = LanguageSpec(
    scopes={
        "class_definition": "class",
        "function_definition": "function",
        "if_statement": "if",
        "elif_clause": "elif",
        "else_clause": "else",
        "for_statement": "for",
        "while_statement": "while",
        "with_statement": "with",
        "try_statement": "try",
        "except_clause": "except",
        "finally_clause": "finally",
        "match_statement": "match",
        "case_clause": "case",
    },
    wrappers=frozenset({"decorated_definition"}),
    load=_load,
)
