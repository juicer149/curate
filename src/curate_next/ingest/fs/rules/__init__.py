"""
Default filesystem rules.
"""

from .registry import PATH_RULES
from .binary import BinaryRule
from .gitignore import GitIgnoreRule
from .manifest import ManifestRule

PATH_RULES.setdefault("binary", BinaryRule)
PATH_RULES.setdefault("gitignore", GitIgnoreRule)
PATH_RULES.setdefault("manifest", ManifestRule)

__all__ = [
    "PATH_RULES",
]
