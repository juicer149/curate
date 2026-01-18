"""
curate.workspace.model — workspace ontology

Defines containers (root/folder/file) and scoped facts.

Core principles:
- folders and files are NOT scopes
- scopes come only from Curate
- hierarchy is encoded purely in NodeId tuples
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple, Mapping, Optional

NodeId = Tuple[int, ...]


class NodeKind(str, Enum):
    ROOT = "root"
    FOLDER = "folder"
    FILE = "file"


@dataclass(frozen=True, slots=True)
class FileUnit:
    """
    A compilation unit for the workspace.
    """

    path: Path
    source: str
    language: Optional[str] = None


@dataclass(frozen=True, slots=True)
class WorkspaceNode:
    """
    A container node (root, folder, file).
    """

    id: NodeId
    kind: NodeKind
    name: str
    path: Path


@dataclass(frozen=True, slots=True)
class WorkspaceScope:
    """
    Curate Scope lifted into workspace hierarchy.
    """

    id: NodeId
    kind: str
    start: int
    end: int
    file_id: NodeId


@dataclass(frozen=True, slots=True)
class Workspace:
    """
    Immutable workspace.

    Invariants:
    - root.id == (0,)
    - root.kind == NodeKind.ROOT
    - every WorkspaceScope.file_id exists and is FILE
    - ids are deterministic for identical inputs
    """

    root: WorkspaceNode
    nodes: Mapping[NodeId, WorkspaceNode]
    path_to_id: Mapping[Path, NodeId]
    scopes: Tuple[WorkspaceScope, ...]
