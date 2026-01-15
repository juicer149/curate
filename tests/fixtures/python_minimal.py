# Canonical minimal Python fixture for Curate.
#
# IMPORTANT:
# - Tests rely on exact line numbers in this file.
# - Do not add/remove lines. Only edit text in-place.

def top():
    """doc"""
    x = 1

    def inner():
        y = x
        return y

    if x:
        z = inner()
        return z

    return None


class C:
    def m(self):
        return 42
