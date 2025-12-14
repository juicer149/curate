from pathlib import Path
import pytest

from curate.api import analyze_file, analyze_text
from curate.query import (
    best_entity_at_line,
    entities_at_line,
    scope_at_line,
    parent_entity,
    direct_children,
)
from curate.views import ViewMode, view_lines
from curate.foldplan import fold_plan_for_view


@pytest.fixture()
def root_scope():
    here = Path(__file__).parent
    p = here / "example_model.py"
    return analyze_file(str(p))


# ------------------------------------------------------------
# best_entity_at_line
# ------------------------------------------------------------

def test_best_entity_at_line_in_module_docstring(root_scope):
    # Line 3 is module docstring summary
    e = best_entity_at_line(root_scope, 3)
    assert e is not None
    assert e.kind == "docstring"
    assert not e.is_code


def test_best_entity_at_line_class_signature(root_scope):
    # Line 12 is: class Example:
    e = best_entity_at_line(root_scope, 12)
    assert e is not None
    assert e.kind == "class"
    assert e.name == "Example"


def test_best_entity_at_line_function_signature(root_scope):
    # Line 21 is: def __init__(...)
    e = best_entity_at_line(root_scope, 21)
    assert e is not None
    assert e.kind == "function"
    assert e.name == "__init__"


# ------------------------------------------------------------
# entities_at_line
# ------------------------------------------------------------

def test_entities_at_line_inside_class_docstring(root_scope):
    hits = entities_at_line(root_scope, 14)
    assert hits
    assert any(h.kind == "docstring" for h in hits)


def test_entities_at_line_inside_function_body(root_scope):
    # Line 29: self.name = name
    hits = entities_at_line(root_scope, 29)
    assert hits
    assert any(h.kind == "function" and h.name == "__init__" for h in hits)


# ------------------------------------------------------------
# Views
# ------------------------------------------------------------

def test_view_minimum_shows_heads_only(root_scope):
    lines = view_lines(root_scope, ViewMode.MINIMUM)
    txt = "\n".join(l.text for l in lines)

    assert "class Example:" in txt
    assert "def __init__" in txt
    assert "def display" in txt

    # Bodies should be hidden
    assert "self.name = name" not in txt
    assert "return f" not in txt


def test_docs_only_shows_docstrings(root_scope):
    lines = view_lines(root_scope, ViewMode.DOCS_ONLY)
    txt = "\n".join(l.text for l in lines)

    assert "A example class with structured data." in txt
    assert "Returns a string representation" in txt
    assert "return f" not in txt


def test_code_only_hides_docstrings(root_scope):
    lines = view_lines(root_scope, ViewMode.CODE_ONLY)
    txt = "\n".join(l.text for l in lines)

    assert "A example class with structured data." not in txt
    assert "Returns a string representation" not in txt
    assert "return f" in txt


# ------------------------------------------------------------
# Fold plan
# ------------------------------------------------------------

def test_fold_plan_minimum_folds_bodies(root_scope):
    plan = fold_plan_for_view(root_scope, ViewMode.MINIMUM)
    assert plan

def test_docstring_head_body_split(root_scope):
    # Klassdocstring
    hits = entities_at_line(root_scope, 14)
    doc = next(e for e in hits if e.kind == "docstring")

    head_text = [l.text.strip() for l in doc.head]
    body_text = [l.text.strip() for l in doc.body]

    assert head_text == ["A example class with structured data."]
    assert "Attributes:" in body_text[0]


def test_scope_at_line_inside_method(root_scope):
    # linter fel: "scope_at_line" is not defined
    scope = scope_at_line(root_scope, 29)  # inside __init__
    # scope should be function scope, not class/module
    texts = [l.text for l in scope.lines]
    assert any("def __init__" in t for t in texts)
    assert not any("class ExampleForTwoClassesInFile" in t for t in texts)

def test_class_owns_methods(root_scope):
    class_entity = best_entity_at_line(root_scope, 12)
    # linter fel: "kind" is not a known attribute of "None"
    assert class_entity.kind == "class"

    # linter fel: Argument of type "Entity | None" cannot be assigned to parameter "entity" of type "Entity" in function "dirext_children" ...
    children = direct_children(root_scope, class_entity)
    names = {e.name for e in children if e.is_code}

    assert "__init__" in names
    assert "display" in names

def test_minimum_fold_inside_class_only(root_scope):
    # linter fel: "scope_at_line" is not defined
    class_scope = scope_at_line(root_scope, 14)
    plan = fold_plan_for_view(class_scope, ViewMode.MINIMUM)

    # Ska inte folda andra klasser eller modul
    folded_lines = {l for r in plan for l in range(r[0], r[1] + 1)}
    assert 42 not in folded_lines  # annan klass

def test_one_line_docstring():
    src = '''
def f():
    """One line."""
    pass
'''
    # linterfel: "analyze_text" is not defined
    scope = analyze_text(src)
    doc = best_entity_at_line(scope, 3)
    # linterfel: "head" is not a known attribute of "None"
    assert doc.head[0].text.strip() == "One line."
    #linterfel: "body" is not a known attribute of "None"
    assert doc.body == ()

