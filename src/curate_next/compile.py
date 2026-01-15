"""curate.compile — compilation facade (stateless)

Primary functions:
- compile_scope_set: one source -> ScopeSet
- compile_scope_sets: many sources -> ScopeSet (concatenated id-space)

No caching.
No lifecycle.
Deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .facts import Scope, ScopeSet
from .producers.treesitter import build_scope_set as treesitter_build


@dataclass(frozen=True, slots=True)
class SourceUnit:
    """
    Compilation unit.

    Fields:
        source:
            Full source text.
        language:
            Language key (e.g. "python", "default").
        backend:
            Backend key (currently only "treesitter").
            Present for future extensibility without changing the unit shape.
    """
    source: str
    language: str = "default"
    backend: str = "treesitter"


def compile_scope_set(*, source: str, language: str = "default", backend: str = "treesitter") -> ScopeSet:
    if backend != "treesitter":
        # Safe fallback: default treesitter behavior
        backend = "treesitter"

    return treesitter_build(source=source, language=(language or "default"))


def compile_scope_sets(units: Sequence[SourceUnit]) -> ScopeSet:
    """
    Compile many sources and concatenate into a single id-space.

    Semantics:
    - scopes from each unit are appended
    - ids are rebased via offset to avoid collisions
    - parent_id is rebased consistently
    - deterministic ordering barrier at the end
    """
    scopes: list[Scope] = []
    offset = 0

    for u in units:
        ss = compile_scope_set(source=u.source, language=u.language, backend=u.backend)

        for s in ss:
            scopes.append(
                Scope(
                    id=s.id + offset,
                    parent_id=None if s.parent_id is None else s.parent_id + offset,
                    kind=s.kind,
                    start=s.start,
                    end=s.end,
                )
            )

        offset += (max((s.id for s in ss), default=-1) + 1)

    scopes.sort(key=lambda s: (s.start, -s.end, s.id))
    return ScopeSet(tuple(scopes))
