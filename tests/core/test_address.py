from curate import Address


def test_root_address():
    root = Address.root()
    assert root.parts == (0,)
    assert root.is_root
    assert root.depth == 0


def test_address_extension_and_parent():
    a = Address.root() + 0
    b = a + 1

    assert a.parts == (0, 0)
    assert b.parts == (0, 0, 1)

    assert b.parent == a
    assert a.parent == Address.root()


def test_prefix_logic():
    root = Address.root()
    a = root + 0
    b = a + 1

    assert root.is_prefix_of(a)
    assert root.is_prefix_of(b)
    assert a.is_prefix_of(b)
    assert not b.is_prefix_of(a)
