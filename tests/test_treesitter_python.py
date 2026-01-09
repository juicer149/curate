from curate.engine import fold


def test_python_basic_scope_self():
    """
    Folding the body of the current function.

    Cursor is inside the function header.
    mode="self" folds the function body itself.
    """
    source = """
def foo():
    x = 1
    y = 2
""".lstrip()

    ranges = fold(
        source=source,
        cursor=1,          # on "def foo():"
        level=0,
        mode="self",
        language="python",
    )

    # Function body spans multiple lines
    assert ranges == ((2, 3),)


def test_python_basic_scope_children_from_module():
    """
    Folding children from module scope.

    Cursor is on the function, but level=1 ascends to module.
    mode="children" then selects the function as a child scope.
    """
    source = """
def foo():
    x = 1
    y = 2
""".lstrip()

    ranges = fold(
        source=source,
        cursor=1,
        level=1,
        mode="children",
        language="python",
    )

    assert ranges == ((2, 3),)


def test_python_decorator_included_in_header():
    """
    Decorators are wrappers:
    they do not create scopes, but extend the header of the function.
    """
    source = """
@decorator
def foo():
    x = 1
    y = 2
""".lstrip()

    ranges = fold(
        source=source,
        cursor=2,
        level=0,
        mode="self",
        language="python",
    )

    # Decorator + def are header, body starts after
    assert ranges == ((3, 4),)


def test_nested_if_as_child_scope():
    """
    Folding child scopes inside a function.

    A foldable scope must span at least two lines.
    """
    source = """
def foo():
    if x > 0:
        print(x)
        print("more")
    print("done")
""".lstrip()

    ranges = fold(
        source=source,
        cursor=1,
        level=0,
        mode="children",
        language="python",
    )

    # Fold only the if-body (two lines)
    assert ranges == ((3, 4),)


def test_unknown_language_falls_back_safely():
    """
    Unknown languages must never crash.
    No semantic guarantees are made.
    """
    source = "just some text\nwith lines"

    ranges = fold(
        source=source,
        cursor=1,
        level=0,
        mode="children",
        language="unknown_language",
    )

    # May return empty or conservative folds, but must be safe
    for start, end in ranges:
        assert 1 <= start < end <= len(source.splitlines())
