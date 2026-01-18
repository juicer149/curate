"""
Curate — Structural Fact Engine.

Curate extracts deterministic, laminar structural facts from syntax trees.

Public surface (core):
- Scope, ScopeSet       — structural facts
- compile_scope_set     — compilation facade
- relations             — algebraic structural relations over facts

Curate intentionally exposes:
- no semantic interpretation
- no policy or filtering
- no query engine
- no file / project / workspace awareness

Curate is designed to act as a stable structural IR
for higher layers that apply meaning and navigation.
"""

from .facts import Scope, ScopeSet
from .compile import compile_scope_set
from . import relations

__all__ = [
    "Scope",
    "ScopeSet",
    "compile_scope_set",
    "relations",
]
