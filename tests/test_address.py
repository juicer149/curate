import pytest

from curate import Address


def test_root_is_empty():
    root = Address.root()
    assert root.parts == ()
    assert root.depth == 0
    assert root.parent is None


def test_child_and_parent():
    a = Address.root().child(0)
    b = a.child(2)
    assert b.parts == (0, 2)
    assert b.depth == 2
    assert b.parent == a
    assert a.parent == Address.root()


def test_prefix_is_ancestry():
    root = Address.root()
    a = root.child(0)
    b = a.child(1)
    c = root.child(1)
    assert root.is_prefix_of(b)
    assert a.is_prefix_of(b)
    assert b.is_prefix_of(b)
    assert not b.is_prefix_of(a)
    assert not c.is_prefix_of(b)


@pytest.mark.parametrize("parts", [(-1,), (0, -2), ("0",)])
def test_rejects_invalid_components(parts):
    with pytest.raises(ValueError):
        Address(parts)


def test_rejects_negative_child_index():
    with pytest.raises(ValueError):
        Address.root().child(-1)
