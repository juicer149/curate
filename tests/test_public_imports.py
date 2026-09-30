def test_curate_public_api_surface():
    import curate

    assert hasattr(curate, "Address")
    assert hasattr(curate, "Scope")
    assert hasattr(curate, "ScopeSet")
    assert hasattr(curate, "compile_scope_set")
    assert hasattr(curate, "relations")
