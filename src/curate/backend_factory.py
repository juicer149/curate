"""
Backend selection.

Place in pipeline:
- engine.fold() calls get_backend()
- maps file_type → backend implementation

This module centralizes language dispatch.
The engine remains backend-agnostic.
"""

from .backend_protocol import Backend
from .backends.python_ast import PythonASTBackend


_BACKENDS: dict[str, type[Backend]] = {
    "python": PythonASTBackend,
}


def get_backend(file_type: str) -> Backend | None:
    """
    Return an instantiated backend for the given file type.

    Unknown file types return None.
    Policy for handling this is owned by the engine or adapter.
    """
    cls = _BACKENDS.get(file_type.lower())
    return cls() if cls else None
