from __future__ import annotations

from .types import Range


def normalize(
    ranges: tuple[Range, ...],
    *,
    max_line: int | None = None,
) -> tuple[Range, ...]:
    """
    Normalize fold ranges into a safe, editor-ready form.

    Guarantees:
    - 1-based inclusive ranges
    - start < end
    - no duplicates
    - sorted
    - optionally clamped to file bounds
    """
    seen: set[Range] = set()
    out: list[Range] = []

    for a, b in ranges:
        if max_line is not None:
            # Clamp to file bounds
            a = min(max(a, 1), max_line)
            b = min(max(b, 1), max_line)

        # Structural validity
        if a >= b:
            continue

        r = (a, b)
        if r in seen:
            continue

        seen.add(r)
        out.append(r)

    out.sort()
    return tuple(out)
