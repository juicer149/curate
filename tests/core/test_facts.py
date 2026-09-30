from curate import Position, RawScope, RawScopeSet, Scope, ScopeSet, Address


def test_position_row_projection():
    p = Position(row=3, col=10)
    assert p.row == 3
    assert p.col == 10


def test_raw_scope_set_is_iterable():
    r = RawScope(
        label="x",
        start=Position(1),
        end=Position(2),
    )

    rs = RawScopeSet([r])
    assert len(rs) == 1
    assert list(rs)[0] is r


def test_scope_set_by_address():
    s1 = Scope(
        address=Address((0,)),
        label="module",
        start=1,
        end=10,
    )
    s2 = Scope(
        address=Address((0, 0)),
        label="child",
        start=2,
        end=5,
    )

    scopes = ScopeSet([s1, s2])

    assert scopes.by_address(Address((0,))) is s1
    assert scopes.by_address(Address((0, 0))) is s2
