from curate import Address, Scope, ScopeSet, relations


def _scopes():
    root = Scope(Address((0,)), "module", 1, 10)
    a = Scope(Address((0, 0)), "a", 2, 5)
    b = Scope(Address((0, 1)), "b", 6, 9)
    c = Scope(Address((0, 0, 0)), "c", 3, 4)

    return ScopeSet([root, a, b, c]), root, a, b, c


def test_parent_relation():
    scopes, _, a, _, c = _scopes()

    assert relations.parent(scopes, c) == a
    assert relations.parent(scopes, a).label == "module"


def test_children_relation():
    scopes, _, a, _, _ = _scopes()

    children = relations.children(scopes, a)
    assert len(children) == 1
    assert children[0].label == "c"


def test_ancestors_relation():
    scopes, _, _, _, c = _scopes()

    ancestors = relations.ancestors(scopes, c)
    assert [s.label for s in ancestors] == ["a", "module"]


def test_descendants_relation():
    scopes, _, a, _, _ = _scopes()

    descendants = relations.descendants(scopes, a)
    assert len(descendants) == 1
    assert descendants[0].label == "c"
