from __future__ import annotations

"""
Tree-sitter language registry.

Maps language identifiers to:
- LanguageRules
- Tree-sitter grammar loaders
"""

from ...policies.python import PYTHON_RULES
from ...policies.default_block import DEFAULT_BLOCK_RULES


LANGUAGE_RULES = {
    "python": PYTHON_RULES,
    "default": DEFAULT_BLOCK_RULES,
}


def load_python_language():
    import tree_sitter_python as tspython
    from tree_sitter import Language
    return Language(tspython.language())


LANGUAGE_LOADERS = {
    "python": load_python_language,
}
