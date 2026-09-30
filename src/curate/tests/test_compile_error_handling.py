from __future__ import annotations

from curate import compile_scopes
from curate.validate import validate_scope_set


def test_compile_scopes_handles_producer_error_and_emits_degenerate_root() -> None:
    errors: list[Exception] = []

    def on_error(e: Exception) -> None:
        errors.append(e)

    ss = compile_scopes(source="ignored", language="default", producer="t_fail", on_error=on_error)

    # Should have called on_error
    assert errors and "intentional failure" in str(errors[0])

    # On error, curate compiles empty RawFactSet → degenerate root [1,1]
    validate_scope_set(ss)
    assert len(ss.scopes) == 1
    root = ss.scopes[0]
    assert root.label == "root"
    assert root.span.start == 1 and root.span.end == 1
