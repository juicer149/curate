"""treesitter.registry — language specs as data

Binds:
- language identifiers
- grammar loader
- structural extraction rules

If loader is None:
- producer falls back to module-only ScopeSet
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .rules import LanguageRules, WrapperRule


@dataclass(frozen=True, slots=True)
class LanguageSpec:
    loader: Optional[Callable[[], "Language"]]
    rules: LanguageRules


def _default_rules() -> LanguageRules:
    return LanguageRules(scope_node_types=frozenset())


# ----------------------------
# Optional loaders (imports inside function)
# ----------------------------

def _load_python():
    import tree_sitter_python as tsp
    from tree_sitter import Language
    return Language(tsp.language())


# ----------------------------
# Minimal structural rulesets
# ----------------------------

PYTHON_RULES = LanguageRules(
    scope_node_types=frozenset(
        {
            # defs
            "class_definition",
            "function_definition",
            # control blocks
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "with_statement",
            "match_statement",
        }
    ),
    wrapper_rules=(
        WrapperRule(
            wrapper_type="decorated_definition",
            target_types=("class_definition", "function_definition"),
        ),
    ),
)

LANGUAGES: dict[str, LanguageSpec] = {
    "default": LanguageSpec(loader=None, rules=_default_rules()),
    "python": LanguageSpec(loader=_load_python, rules=PYTHON_RULES),
}
