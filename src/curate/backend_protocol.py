"""
Curate backend protocol.

This module defines the contract that all structural backends must implement.

Place in pipeline:
- engine.fold() (engine.py) selects a backend via the factory.
- engine.fold() delegates folding to backend.fold().
- engine normalizes the returned ranges.

Backend invariants:
- level == 0 MUST target the smallest structural scope containing the cursor.
  (How that scope is folded depends on fold_children.)

Inputs are pure data:
- content: full source text
- cursor:  1-based cursor line
- level:   >= 0, interpreted by the backend (level=0 is mandatory)
- fold_children:
    - True  => fold bodies of the target node's children (keep their headers visible)
    - False => fold the body of the target node itself (keep its header visible)

Output:
- Iterable[Range] where Range is (start_line, end_line), inclusive, 1-based.
"""

from typing import Iterable, Protocol

from .types import Range


class Backend(Protocol):
    def fold(
        self,
        *,
        content: str,
        cursor: int,
        level: int,
        fold_children: bool,
    ) -> Iterable[Range]:
        ...
