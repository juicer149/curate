"""
Engine orchestration.

C philosophy
------------
This module coordinates components but never decides semantics.

It wires together:
- structure production
- indexing
- intent evaluation
- normalization

Design principle
----------------
"The engine is the referee, not the player."
"""

from __future__ import annotations

from .types import Range, FoldMode
from .rules import PYTHON_RULES, NO_FOLD_RULES, Rules
from .index import build_index
from .evaluator import Intent, evaluate
from .normalize import normalize
from .producers import get_producer


_RULES_BY_LANGUAGE: dict[str, Rules] = {
    "python": PYTHON_RULES,
}


def fold(
    *,
    source: str,
    cursor: int,
    level: int,
    mode: FoldMode,
    language: str = "python",
) -> tuple[Range, ...]:
    """
    Compute fold ranges for a given source and intent.
    """
    producer = get_producer(language)
    rules = _RULES_BY_LANGUAGE.get(language, NO_FOLD_RULES)

    graph = producer(source)
    idx = build_index(graph)
    intent = Intent(cursor=cursor, level=level, mode=mode)

    ranges = evaluate(graph, idx, rules, intent)
    return normalize(ranges)
