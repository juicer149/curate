from __future__ import annotations

from .types import FoldMode, Range
from .evaluator import Intent, evaluate
from .index import build_index
from .normalize import normalize
from .producers import get_producer


def fold(
    *,
    source: str,
    cursor: int,
    level: int,
    mode: FoldMode,
    language: str = "python",
) -> tuple[Range, ...]:
    # IMPORTANT:
    # Use splitlines() to match how tests (and many editors) count lines.
    # This avoids off-by-one when the source ends with a trailing newline.
    total_lines = len(source.splitlines()) if source else 1
    total_lines = max(1, total_lines)

    graph = get_producer(language)(source)
    idx = build_index(graph)
    intent = Intent(cursor=cursor, level=level, mode=mode)

    raw = evaluate(graph, idx, intent)
    return normalize(raw, max_line=total_lines)

# add in doc:
# Line numbers are defined using Python's splitlines().
# A trailing newline does not create an extra addressable line.
