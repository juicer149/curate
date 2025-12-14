from enum import Enum, auto
from typing import Iterable, List

from .line import Line
from .scope import Scope


class ViewMode(Enum):
    MINIMUM = auto()
    CODE_ONLY = auto()
    DOCS_ONLY = auto()
    FULL = auto()


def view_lines(scope: Scope, mode: ViewMode) -> List[Line]:
    """
    Produce a linear list of lines for a given view mode.

    IMPORTANT:
    Views operate ONLY on line kinds.
    Entities and scopes are NOT consulted here.
    """

    lines: Iterable[Line] = scope.lines

    if mode == ViewMode.FULL:
        return list(lines)

    if mode == ViewMode.CODE_ONLY:
        return [
            l for l in lines
            if "code" in l.kinds and "doc" not in l.kinds
        ]

    if mode == ViewMode.DOCS_ONLY:
        return [
            l for l in lines
            if "doc" in l.kinds
        ]

    if mode == ViewMode.MINIMUM:
        # MINIMUM is special: only show heads of code entities
        seen = set()
        out = []

        def walk(s: Scope):
            for e in s.entities:
                for l in e.head:
                    if l.number not in seen:
                        seen.add(l.number)
                        out.append(l)
            for c in s.children:
                walk(c)

        walk(scope)
        return sorted(out, key=lambda l: l.number)

    raise ValueError(f"Unhandled ViewMode: {mode}")
