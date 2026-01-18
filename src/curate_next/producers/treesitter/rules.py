"""
treesitter.rules — rule schema

Rules describe *which syntax nodes become scopes*.

They do NOT describe meaning.
"""

from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True, slots=True)
class LanguageRules:
    include: FrozenSet[str]
    exclude: FrozenSet[str]
    only_multiline: bool

    @classmethod
    def from_dict(cls, d: dict) -> "LanguageRules":
        scopes = d.get("scopes", {})
        return cls(
            include=frozenset(scopes.get("include", [])),
            exclude=frozenset(scopes.get("exclude", [])),
            only_multiline=bool(scopes.get("only_multiline", False)),
        )
