"""
curate.workspace.language — language resolution

Pure metadata resolution.
No parsing. No interpretation.
"""

from dataclasses import dataclass
from typing import Mapping, Optional
from .model import FileUnit


@dataclass(frozen=True, slots=True)
class LanguageResolver:
    """
    Deterministic language resolver.

    Resolution order:
    1) explicit FileUnit.language
    2) extension map
    3) shebang heuristic (optional)
    4) default_language
    """

    extension_map: Mapping[str, str]
    default_language: str = "default"
    enable_shebang: bool = True

    def resolve(self, unit: FileUnit) -> str:
        if unit.language:
            return unit.language

        suffix = unit.path.suffix.lower()
        if suffix in self.extension_map:
            return self.extension_map[suffix]

        if self.enable_shebang:
            sb = _detect_from_shebang(unit.source)
            if sb is not None:
                return sb

        return self.default_language


def _detect_from_shebang(source: str) -> Optional[str]:
    if not source.startswith("#!"):
        return None

    first = source.splitlines()[0].lower()

    if "python" in first:
        return "python"
    if "lua" in first:
        return "lua"

    return None


def default_language_resolver() -> LanguageResolver:
    return LanguageResolver(
        extension_map={
            ".py": "python",
            ".lua": "lua",
            ".rs": "rust",
            ".js": "javascript",
            ".ts": "typescript",
        },
        default_language="default",
        enable_shebang=True,
    )
