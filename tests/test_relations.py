from pathlib import Path

from curate.index import build_index
from curate.producers import get_producer
from curate.query import resolve_scopes, query_from_dict

SRC = Path(__file__).parent / "fixtures/python_minimal.py"
TEXT = SRC.read_text(encoding="utf-8")


def run(cursor: int, qdict: dict):
    producer = get_producer("python")
    graph = producer(TEXT)
    idx = build_index(graph)
    q = query_from_dict(cursor=cursor, d=qdict)
    return resolve_scopes(graph, idx, q)


def kinds(scopes):
    return tuple(s.kind for s in scopes)


def test_self_on_top_function():
    scopes = run(7, {"axis": "self"})
    assert kinds(scopes) == ("function",)


def test_children_of_top():
    scopes = run(7, {"axis": "children"})
    assert set(kinds(scopes)) == {"function", "if"}


def test_parent_of_inner():
    scopes = run(12, {"axis": "parent"})
    assert kinds(scopes) == ("function",)


def test_ancestors_of_inner():
    scopes = run(12, {"axis": "ancestors", "include_target": True})
    assert kinds(scopes) == ("function", "function", "module")


def test_siblings_of_inner():
    scopes = run(12, {"axis": "siblings"})
    assert kinds(scopes) == ("if",)


def test_all_functions():
    scopes = run(1, {"axis": "all_of_kind", "kind": "function"})
    assert kinds(scopes) == ("function", "function", "function")
