# tests/test_example_file.py

from pathlib import Path

import pytest

from curate_next import compile_scope_set, relations
from curate_next.facts import Scope, ScopeSet
from curate_next.workspace import (
    FileUnit,
    build_workspace,
    scopes_in_file,
    parent_of,
    children_of,
)


# ---------------------------------------------------------------------------
# Example source (single source of truth for all tests)
# ---------------------------------------------------------------------------

SRC = """
\"\"\"
Module docstring
\"\"\"

class Foo:
    \"\"\"
    Class docstring
    \"\"\"

    def bar(self, x):
        \"\"\"
        Function docstring
        \"\"\"
        if x > 0:
            return x
        else:
            return -x
""".strip()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_scopes() -> ScopeSet:
    return compile_scope_set(source=SRC, language="python")


def scope_by_label(scopes: ScopeSet, label: str) -> list[Scope]:
    return [s for s in scopes if s.label == label]


# ---------------------------------------------------------------------------
# Core tests (facts + compilation)
# ---------------------------------------------------------------------------

def test_compile_produces_root_scope():
    scopes = build_scopes()

    root = scopes[0]
    assert root.id == (0,)
    assert root.label == "module"
    assert root.start == 1
    assert root.end >= root.start


def test_scopes_are_laminar_and_ordered():
    scopes = build_scopes()

    for s in scopes:
        # id invariant
        assert len(s.id) >= 1
        # span invariant
        assert s.start <= s.end

    # deterministic ordering invariant
    for a, b in zip(scopes, scopes[1:]):
        assert (a.start, -a.end, a.id) <= (b.start, -b.end, b.id)


def test_expected_scope_labels_exist():
    scopes = build_scopes()
    labels = {s.label for s in scopes}

    assert "module" in labels
    assert "class_definition" in labels
    assert "function_definition" in labels
    assert "if_statement" in labels
    assert "string" in labels  # docstrings


# ---------------------------------------------------------------------------
# Relations tests (purely structural)
# ---------------------------------------------------------------------------

def test_parent_relationship_is_algebraic():
    scopes = build_scopes()

    func = scope_by_label(scopes, "function_definition")[0]
    parent = relations.parent(scopes, func)

    assert parent is not None
    assert parent.id == func.parent_id


def test_function_is_nested_in_class_via_ancestors():
    scopes = build_scopes()

    func = scope_by_label(scopes, "function_definition")[0]
    labels = [s.label for s in relations.ancestors(scopes, func)]

    assert "class_definition" in labels
    assert labels[-1] == "module"


def test_ancestors_chain_order_and_content():
    scopes = build_scopes()

    if_scope = scope_by_label(scopes, "if_statement")[0]
    ancestors = relations.ancestors(scopes, if_scope)

    # nearest first, root last
    assert ancestors[-1].label == "module"
    assert any(s.label == "function_definition" for s in ancestors)
    assert any(s.label == "class_definition" for s in ancestors)


def test_descendants_are_prefix_based():
    scopes = build_scopes()

    cls = scope_by_label(scopes, "class_definition")[0]
    desc = relations.descendants(scopes, cls)

    assert desc
    assert all(s.id[: len(cls.id)] == cls.id for s in desc)
    assert any(s.label == "function_definition" for s in desc)


# ---------------------------------------------------------------------------
# Workspace tests
# ---------------------------------------------------------------------------

def test_workspace_build_and_file_node(tmp_path: Path):
    file_path = tmp_path / "example.py"

    unit = FileUnit(
        path=file_path,
        source=SRC,
        language="python",
    )

    ws = build_workspace(files=[unit], root=tmp_path)

    # workspace root represents the filesystem root folder
    assert ws.root.id == (0,)
    assert ws.root.label.value == "folder"
    assert ws.root.path == tmp_path.resolve()

    # file node exists
    file_id = ws.path_to_id[file_path]
    file_node = ws.nodes[file_id]

    assert file_node.label.value == "file"
    assert file_node.name == "example.py"
    assert file_node.path == file_path.resolve()


def test_workspace_scopes_prefixed_with_file_id(tmp_path: Path):
    file_path = tmp_path / "example.py"

    unit = FileUnit(
        path=file_path,
        source=SRC,
        language="python",
    )

    ws = build_workspace(files=[unit], root=tmp_path)
    file_id = ws.path_to_id[file_path]

    scopes = scopes_in_file(ws, file_path)
    assert scopes

    for s in scopes:
        assert s.id[: len(file_id)] == file_id


def test_workspace_parent_child_hierarchy(tmp_path: Path):
    file_path = tmp_path / "example.py"

    unit = FileUnit(
        path=file_path,
        source=SRC,
        language="python",
    )

    ws = build_workspace(files=[unit], root=tmp_path)
    file_id = ws.path_to_id[file_path]

    # file -> workspace root (folder)
    parent = parent_of(ws, file_id)
    assert parent is not None
    assert parent.id == ws.root.id
    assert parent.label.value == "folder"

    # workspace root has no parent
    assert parent_of(ws, parent.id) is None

    # root children include file
    children = children_of(ws, ws.root.id)
    assert any(ch.id == file_id for ch in children)
