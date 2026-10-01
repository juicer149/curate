# examples/demo.py — the core on hand-made facts (no tree-sitter needed).
# Run: .venv/bin/python examples/demo.py
from __future__ import annotations

from curate import RawFact, Span, compile_scopes
from curate.facts import RawFactSet
from curate.producers.registry import register
from curate.relations import ancestors, children, descendants


def demo_producer(*, source: str, language: str) -> RawFactSet:
    # Example facts: nested + disjoint structure over integer coordinates
    facts = [
        RawFact("A", Span(10, 50)),
        RawFact("B", Span(15, 30)),
        RawFact("C", Span(35, 45)),
        RawFact("D", Span(60, 70)),  # disjoint
        # Duplicate geometry example (will be dropped by policy):
        RawFact("A_DUP", Span(10, 50)),
        # Crossing example (will be rejected by laminar policy if present alongside A):
        # RawFact("X", Span(25, 60)),
    ]
    return RawFactSet.from_iter(facts)


# Register under a name
register("demo", lambda: demo_producer)


def main() -> None:
    ss = compile_scopes(source="ignored", language="default", producer="demo")

    print("Scopes:")
    for s in ss.scopes:
        print(f"  {s.address.parts!s:>10}  {s.label:<8}  [{s.span.start}, {s.span.end}]")

    root = ss.scopes[0]
    print("\nchildren(root):", [c.label for c in children(ss, root)])

    A = next(s for s in ss.scopes if s.label == "A")
    print("children(A):", [c.label for c in children(ss, A)])
    print("descendants(A):", [d.label for d in descendants(ss, A)])

    B = next(s for s in ss.scopes if s.label == "B")
    print("ancestors(B):", [a.label for a in ancestors(ss, B)])


if __name__ == "__main__":
    main()
