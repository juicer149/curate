"""
One file per language.

Each module in this package describes one Tree-sitter language:

    NAMES       names it answers to; the first is the canonical name
    EXTENSIONS  file suffixes, e.g. (".py",)
    SPEC        a LanguageSpec

Lookup by name is by convention: language "python" is the module
python.py, imported directly. Aliases ("py") and file suffixes (".md")
fall back to an index built once from every module's NAMES and
EXTENSIONS. Adding a language is adding a file; nothing is registered.
"""

from __future__ import annotations

import pkgutil
from functools import lru_cache
from importlib import import_module
from pathlib import PurePath
from types import ModuleType
from typing import Optional

from ..spec import LanguageSpec


def _module(name: str) -> Optional[ModuleType]:
    """Import languages/<name>.py, or None if there is no such file."""
    if not name.isidentifier() or name.startswith("_"):
        return None
    qualified = f"{__name__}.{name}"
    try:
        return import_module(qualified)
    except ModuleNotFoundError as e:
        if e.name == qualified:
            return None
        raise  # the file exists but something it imports is missing


@lru_cache(maxsize=1)
def _index() -> tuple[dict[str, str], dict[str, str]]:
    """(alias -> module name, suffix -> module name) over all language files."""
    names: dict[str, str] = {}
    suffixes: dict[str, str] = {}
    for info in pkgutil.iter_modules(__path__):
        module = _module(info.name)
        if module is None:
            continue
        for alias in getattr(module, "NAMES", (info.name,)):
            names.setdefault(alias.lower(), info.name)
        for suffix in getattr(module, "EXTENSIONS", ()):
            suffixes.setdefault(suffix.lower(), info.name)
    return names, suffixes


def resolve(language: str) -> Optional[str]:
    """Canonical module name for a language name or alias, or None."""
    key = (language or "").strip().lower()
    if not key:
        return None
    if _module(key) is not None:
        return key
    return _index()[0].get(key)


def get_spec(language: str) -> Optional[LanguageSpec]:
    """The LanguageSpec for a language name or alias, or None if unknown."""
    name = resolve(language)
    if name is None:
        return None
    module = _module(name)
    return getattr(module, "SPEC", None)


def language_for_path(path: str) -> Optional[str]:
    """Canonical language name for a file path, from its suffix, or None."""
    suffix = PurePath(path).suffix.lower()
    if not suffix:
        return None
    name = _index()[1].get(suffix)
    if name is None:
        return None
    module = _module(name)
    return getattr(module, "NAMES", (name,))[0]
