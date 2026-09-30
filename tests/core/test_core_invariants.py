from curate import compile_scope_set


def test_compile_is_total():
    scopes = compile_scope_set(source="", language="default", producer="noop")

    assert len(scopes) == 1
    root = scopes[0]
    assert root.label == "module"
    assert root.start == 1
    assert root.end == 1
