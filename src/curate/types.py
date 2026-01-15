from __future__ import annotations

from typing import Literal, TypedDict

Range = tuple[int, int]

Axis = Literal[
    "self",
    "parent",
    "children",
    "ancestors",
    "descendants",
    "siblings",
    "next",
    "prev",
    "next_same_kind",
    "prev_same_kind",
    "all_of_kind",
]

FoldMode = Literal["self", "children", "parent", "ancestors", "descendants"]


class QueryDict(TypedDict, total=False):
    axis: Axis

    # filters
    kinds: tuple[str, ...] | list[str]
    include_target: bool
    max_items: int | None

    # axis-specific parameters
    kind: str  # for all_of_kind
