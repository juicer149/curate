"""
curate_core.ingest

Ingest adapters normalize external structures into Curate's
internal container geometry.

Responsibilities:
- adapt foreign hierarchies (filesystem, APIs, manifests, etc.)
- apply selection + ordering policy
- emit ContainerTree with deterministic Address assignment

Ingest does NOT:
- parse source code
- infer language
- produce scopes
- manage editor or AI state
"""

from .fs import ingest_filesystem

__all__ = [
    "ingest_filesystem",
]
