# tests/utils.py
import random
from typing import Iterable, List


def seeded_lines_from(
    lines: Iterable[int],
    *,
    seed: int,
    count: int | None = None,
) -> List[int]:
    """
    Return a deterministic subset of line numbers.

    - Same seed => same result
    - Sorted for stable test output
    """
    rnd = random.Random(seed)
    lines = list(lines)

    if not lines:
        return []

    if count is None or count >= len(lines):
        return sorted(lines)

    return sorted(rnd.sample(lines, count))
