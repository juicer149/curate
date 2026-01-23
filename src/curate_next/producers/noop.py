# curate_next/producers/noop.py

from ..facts import Scope, ScopeSet


def build_scope_set(*, source: str, language: str) -> ScopeSet:
    """
    Fallback producer.

    Produces a single module-level scope covering the entire source.
    """
    lines = source.splitlines()
    end = max(len(lines), 1)

    return ScopeSet((
        Scope(
            address=(0,),
            label="module",
            start=1,
            end=end,
        ),
    ))
