import pytest
from curate import compile_scope_set

pytestmark = pytest.mark.treesitter


def _require_treesitter():
    pytest.importorskip("tree_sitter")
    pytest.importorskip("tree_sitter_python")


SRC = """
class Foo:
    def bar(self, x):
        if x > 0:
            return x
        return -x
""".strip()


def build_scopes():
    _require_treesitter()
    return tuple(
        compile_scope_set(
            source=SRC,
            language="python",
            producer="treesitter",
        )
    )


def test_expected_labels_exist():
    scopes = build_scopes()
    labels = {s.label for s in scopes}

    assert "module" in labels
    assert "class_definition" in labels
    assert "function_definition" in labels
    assert "if_statement" in labels


def test_nesting_via_prefix():
    scopes = build_scopes()

    cls = next(s for s in scopes if s.label == "class_definition")
    func = next(s for s in scopes if s.label == "function_definition")
    ifs = next(s for s in scopes if s.label == "if_statement")

    assert cls.address.is_prefix_of(func.address)
    assert func.address.is_prefix_of(ifs.address)
