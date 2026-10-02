from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from curate.__main__ import main

FIXTURES = Path(__file__).resolve().parent / "fixtures"
FIXTURE = FIXTURES / "python_minimal.py"


def test_chain_json_contract(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("ignored"))
    assert main(["chain", "-", "--line", "20", "--language", "demo", "--producer", "t_demo"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {
        "line": 20,
        "chain": [
            {"address": [0, 0], "label": "B", "start": 15, "end": 30, "outline": None},
            {"address": [0], "label": "A", "start": 10, "end": 50, "outline": None},
        ],
    }


def test_failing_producer_exits_nonzero(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("ignored"))
    assert main(["chain", "-", "--line", "1", "--language", "demo", "--producer", "t_fail"]) == 1
    assert "intentional failure" in capsys.readouterr().err


@pytest.mark.treesitter
def test_chain_on_python_fixture(capsys):
    pytest.importorskip("tree_sitter_python")
    assert main(["chain", str(FIXTURE), "--line", "16"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [(c["label"], c["start"], c["end"]) for c in out["chain"]] == [
        ("if", 15, 17),
        ("function", 7, 19),
    ]


def test_stdin_without_language_is_an_error(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("x = 1\n"))
    assert main(["chain", "-", "--line", "1"]) == 2
    assert "pass --language" in capsys.readouterr().err


def test_unknown_suffix_without_language_is_an_error(tmp_path, capsys):
    path = tmp_path / "notes.xyz"
    path.write_text("hello\n")
    assert main(["chain", str(path), "--line", "1"]) == 2
    assert "notes.xyz" in capsys.readouterr().err


@pytest.mark.treesitter
def test_chain_on_markdown_fixture_infers_language(capsys):
    pytest.importorskip("tree_sitter_markdown")
    assert main(["chain", str(FIXTURES / "markdown_minimal.md"), "--line", "9"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [(c["label"], c["start"], c["end"]) for c in out["chain"]] == [
        ("h3", 9, 12),
        ("h2", 5, 12),
        ("h1", 1, 16),
    ]


def test_unknown_language_is_an_error(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("x\n"))
    assert main(["chain", "-", "--line", "1", "--language", "lua"]) == 2
    assert "no structure support for language 'lua'" in capsys.readouterr().err


@pytest.mark.parametrize("alias", ["py", "Python"])
def test_language_aliases_are_accepted(monkeypatch, alias):
    pytest.importorskip("tree_sitter_python")
    monkeypatch.setattr("sys.stdin", io.StringIO("def f():\n    pass\n"))
    assert main(["chain", "-", "--line", "2", "--language", alias]) == 0


@pytest.mark.treesitter
def test_chain_reports_outline_kind(capsys):
    pytest.importorskip("tree_sitter_python")
    assert main(["chain", str(FIXTURE), "--line", "23"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [(c["label"], c["outline"]) for c in out["chain"]] == [
        ("function", "closed"),
        ("class", "open"),
    ]


@pytest.mark.treesitter
def test_decorated_definitions_report_their_head(monkeypatch, capsys):
    pytest.importorskip("tree_sitter_python")
    src = "@dataclass\nclass A:\n    x: int\n\n    def m(self):\n        pass\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(src))
    assert main(["outline", "-", "--language", "python"]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "folds": [{"start": 1, "end": 4, "head": 2}, {"start": 5, "end": 6}],
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(src))
    assert main(["chain", "-", "--line", "6", "--language", "python"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [(c["label"], c["start"], c.get("head")) for c in out["chain"]] == [
        ("function", 5, None),
        ("class", 1, 2),
    ]


@pytest.mark.treesitter
def test_outline_python_fixture(capsys):
    pytest.importorskip("tree_sitter_python")
    assert main(["outline", str(FIXTURE)]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "folds": [{"start": 7, "end": 19}, {"start": 23, "end": 24}],
    }


@pytest.mark.treesitter
def test_outline_closed_folds_classes_whole(capsys):
    pytest.importorskip("tree_sitter_python")
    assert main(["outline", str(FIXTURE), "--closed"]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "folds": [{"start": 7, "end": 19}, {"start": 22, "end": 24}],
    }


@pytest.mark.treesitter
def test_outline_markdown_fixture(capsys):
    pytest.importorskip("tree_sitter_markdown")
    assert main(["outline", str(FIXTURES / "markdown_minimal.md")]) == 0
    folds = json.loads(capsys.readouterr().out)["folds"]
    assert [(f["start"], f["end"]) for f in folds] == [(1, 4), (5, 8), (9, 12), (13, 16), (17, 19)]


def test_outline_needs_a_language(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("x\n"))
    assert main(["outline", "-"]) == 2
    assert "pass --language" in capsys.readouterr().err
