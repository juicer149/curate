from __future__ import annotations

import pytest

from curate import RawFact, Span
from curate.facts import RawFactSet
from curate.producers.registry import register


@pytest.fixture(autouse=True, scope="session")
def register_test_producer() -> None:
    """
    Register a test producer ('t_demo') that emits a laminar set:
      A: [10, 50]
      B: [15, 30]    (child of A)
      C: [35, 45]    (child of A)
      D: [60, 70]    (disjoint from A)
    Also registers a failing producer ('t_fail') to test error handling.
    """

    def t_demo(*, source: str, language: str) -> RawFactSet:
        facts = [
            RawFact("A", Span(10, 50)),
            RawFact("B", Span(15, 30)),
            RawFact("C", Span(35, 45)),
            RawFact("D", Span(60, 70)),
            # Duplicate (policy should drop it deterministically)
            RawFact("A_DUP", Span(10, 50)),
        ]
        return RawFactSet.from_iter(facts)

    def t_fail(*, source: str, language: str) -> RawFactSet:
        raise RuntimeError("intentional failure")

    register("t_demo", lambda: t_demo)
    register("t_fail", lambda: t_fail)
