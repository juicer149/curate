"""
curate_next — INTERNAL structural IR implementation.

INTERNAL PACKAGE — NOT A STABLE API

This package contains the current implementation of Curate's
structural intermediate representation.

External consumers MUST NOT import from `curate_next`.
Use the `curate` package instead.

This module exists to:
- support internal development
- allow iterative refactoring
- enable a future rename to `curate_core`

No stability guarantees are provided here.
"""

from .address import Address
from .facts import Position, RawScope, RawScopeSet, Scope, ScopeSet
from .compile import compile_scope_set
from . import relations

__all__ = [
    "Address",
    "Position",
    "RawScope",
    "RawScopeSet",
    "Scope",
    "ScopeSet",
    "compile_scope_set",
    "relations",
]
