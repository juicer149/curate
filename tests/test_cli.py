from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from curate.__main__ import main

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "python_minimal.py"


def test_chain_json_contract(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("ignored"))
    assert main(["chain", "-", "--line", "20", "--producer", "t_demo"]) == 0
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
    assert main(["chain", "-", "--line", "1", "--producer", "t_fail"]) == 1
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
