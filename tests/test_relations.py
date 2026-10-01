from __future__ import annotations

from curate import compile_scopes
from curate.relations import parent, children, ancestors, descendants


def test_relations_on_demo() -> None:
    ss = compile_scopes(source="ignored", language="default", producer="t_demo")

    # Ensure we have expected labels
    labels = [s.label for s in ss.scopes]
    assert "root" in labels and "A" in labels and "B" in labels and "C" in labels and "D" in labels

    root = ss.scopes[0]
    cs_root = [c.label for c in children(ss, root)]
    assert cs_root == ["A", "D"]

    A = next(s for s in ss.scopes if s.label == "A")
    B = next(s for s in ss.scopes if s.label == "B")

    assert [c.label for c in children(ss, A)] == ["B", "C"]
    assert [d.label for d in descendants(ss, A)] == ["B", "C"]
    assert [a.label for a in ancestors(ss, B)] == ["A", "root"]

    # Parent utility works
    assert parent(ss, A) == root
