"""
Registry for Tree-sitter language support.

This module is the single place where:
- language identifiers
- grammar loaders
- structural scope rules

are bound together.
"""
from __future__ import annotations

from typing import Callable, Optional
from tree_sitter import Language

from .rules import LanguageRules
from .languages import python, default


class LanguageSpec:
    """
    Complete Tree-sitter language specification.

    rules:
        Structural rules describing how syntax nodes map to scopes.

    loader:
        Callable that loads and returns a Tree-sitter Language.
        If None, this language cannot be parsed and will produce
        an empty scope graph.
    """
    def __init__(
        self,
        *,
        rules: LanguageRules,
        loader: Optional[Callable[[], Language]],
    ):
        self.rules = rules
        self.loader = loader


LANGUAGES: dict[str, LanguageSpec] = {
    "python": LanguageSpec(
        rules=python.PYTHON_RULES,
        loader=python.load_language,
    ),
    "default": LanguageSpec(
        rules=default.DEFAULT_RULES,
        loader=None,
    ),
}
