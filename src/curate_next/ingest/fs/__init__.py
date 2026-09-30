"""
curate_core.ingest.fs

Filesystem ingestion adapter.

Maps:
    OS filesystem → ContainerTree

Policy is injected via rules.
Geometry is delegated to containers.
"""

from .adapter import ingest_filesystem

__all__ = [
    "ingest_filesystem",
]
