"""
Folding rules (policy as data).

Lisp analogy
------------
In Lisp, behavior is data.
This module follows the same idea.

Rules are:
- explicit
- immutable
- passed as values
- evaluated mechanically

Why this exists
---------------
- Avoid hard-coded conditionals
- Allow multiple rule sets in parallel
- Enable editor- or language-specific policies

Design principle
----------------
"Rules describe behavior. Evaluation applies them."
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from .model import Scope


@dataclass(frozen=True)
class Rules:
    """
    A complete folding policy.

    All semantics live here.
    """
    header_size: Callable[[Scope], int]
    navigable: Callable[[Scope], bool]
    foldable: Callable[[Scope], bool]


def python_header_size(scope: Scope) -> int:
    """
    Compute header size for Python scopes.

    Docstring semantics:
    - length <= 3 → no foldable body
    - length > 3  → header is exactly 3 lines

    Code semantics:
    - header is always 1 line
    """
    if scope.role == "doc":
        if scope.length <= 3:
            return scope.length
        return 3
    return 1


# Python-specific folding policy
PYTHON_RULES = Rules(
    header_size=python_header_size,
    navigable=lambda s: s.role != "doc",
    foldable=lambda s: True,
)


# Safe fallback policy for unsupported languages
NO_FOLD_RULES = Rules(
    header_size=lambda s: s.length,
    navigable=lambda s: False,
    foldable=lambda s: False,
)
