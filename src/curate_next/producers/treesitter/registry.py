"""treesitter.registry — language registry

Binds:
- language key
- grammar loader
- structural rules (loaded from .lang.json)
"""

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Callable, Optional

from .rules import LanguageRules


@dataclass(frozen=True, slots=True)
class LanguageSpec:
    loader: Optional[Callable]
    rules: LanguageRules


def _load_python():
    import tree_sitter_python as tsp
    from tree_sitter import Language
    return Language(tsp.language())


def _load_rules(name: str) -> LanguageRules:
    path = Path(__file__).parent / "languages" / f"{name}.lang.json"
    with path.open("r", encoding="utf-8") as f:
        return LanguageRules.from_dict(json.load(f))


LANGUAGES = {
    "default": LanguageSpec(
        loader=None,
        rules=_load_rules("default"),
    ),
    "python": LanguageSpec(
        loader=_load_python,
        rules=_load_rules("python"),
    ),
}
