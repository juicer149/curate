from __future__ import annotations

from .types import Range


def normalize_ranges(
    ranges: tuple[Range, ...],
    *,
    total_lines: int,
) -> tuple[Range, ...]:
    """
    Normalize a set of line ranges.

    Guarantees:
    - all ranges are (int, int)
    - 1 <= start < end <= total_lines
    - no duplicates
    - sorted by (start, end)

    This function is the FINAL safety barrier.
    """
    if total_lines <= 0:
        total_lines = 1

    out: list[Range] = []
    seen: set[Range] = set()

    for a, b in ranges:
        if not isinstance(a, int) or not isinstance(b, int):
            continue

        # Clamp to bounds
        a = max(1, min(a, total_lines))
        b = max(1, min(b, total_lines))

        # Enforce strict ordering
        if a >= b:
            continue

        r = (a, b)
        if r in seen:
            continue

        seen.add(r)
        out.append(r)

    out.sort(key=lambda r: (r[0], r[1]))
    return tuple(out)
