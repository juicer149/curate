"""The real Python grammar on the line-exact fixture."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter_python")

from curate import compile_scopes  # noqa: E402
from curate.relations import chain  # noqa: E402
from curate.validate import validate_scope_set  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "python_minimal.py"
pytestmark = pytest.mark.treesitter


def _scopes():
    return compile_scopes(source=FIXTURE.read_text(), language="python", producer="treesitter")


def test_fixture_scopes_and_lines():
    ss = _scopes()
    validate_scope_set(ss)
    found = sorted((s.label, s.span.start, s.span.end) for s in ss.scopes if s.label != "root")
    assert found == sorted([
        ("function", 7, 19),   # top
        ("function", 11, 13),  # inner
        ("if", 15, 17),
        ("class", 22, 24),
        ("function", 23, 24),  # m
    ])


def test_chain_zooms_out_from_cursor():
    ss = _scopes()
    assert [(s.label, s.span.start) for s in chain(ss, 16)] == [("if", 15), ("function", 7)]
    assert [(s.label, s.span.start) for s in chain(ss, 24)] == [("function", 23), ("class", 22)]
    assert chain(ss, 21) == ()


def test_decorated_function_starts_at_decorator():
    src = "@dec\ndef f():\n    return 1\n"
    ss = compile_scopes(source=src, language="python", producer="treesitter")
    assert [(s.label, s.span.start, s.span.end) for s in ss.scopes if s.label != "root"] == [
        ("function", 1, 3),
    ]


def test_unknown_language_yields_only_root():
    ss = compile_scopes(source="x = 1\n", language="cobol", producer="treesitter")
    assert [s.label for s in ss.scopes] == ["root"]
