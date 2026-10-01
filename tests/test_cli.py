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
            {"address": [0, 0], "label": "B", "start": 15, "end": 30},
            {"address": [0], "label": "A", "start": 10, "end": 50},
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
