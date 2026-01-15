# src/curate/evaluator.py
from __future__ import annotations

from .model import Scope
from .types import Range


def ranges_for_scopes(scopes: tuple[Scope, ...]) -> tuple[Range, ...]:
    """
    Convert scopes into foldable body ranges.

    May return invalid / empty ranges.
    Normalization is handled by the engine layer.
    """
    out: list[Range] = []

    for scope in scopes:
        r = scope.body_range()
        if r is not None:
            out.append(r)

    return tuple(out)
