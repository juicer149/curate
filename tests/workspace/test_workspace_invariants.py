from pathlib import Path
from curate import Address, build_workspace
from curate.workspace import FileUnit


def test_workspace_rebases_scopes():
    unit = FileUnit(
        path=Path("example.py"),
        source="x = 1\ny = 2\n",
        producer="noop",
    )

    ws = build_workspace(files=[unit])

    assert ws.root.address.is_root
    assert len(ws.scopes) == 1

    scope = ws.scopes[0]
    assert not scope.address.is_root

    file_node = next(
        n for n in ws.nodes.values()
        if n.kind.name.lower() == "file"
    )

    assert file_node.address.is_prefix_of(scope.address)


def test_multiple_files_are_disjoint():
    f1 = FileUnit(
        path=Path("a.py"),
        source="a = 1\n",
        producer="noop",
    )
    f2 = FileUnit(
        path=Path("b.py"),
        source="b = 2\n",
        producer="noop",
    )

    ws = build_workspace(files=[f1, f2])

    a, b = ws.scopes
    assert not a.address.is_prefix_of(b.address)
    assert not b.address.is_prefix_of(a.address)
