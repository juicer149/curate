"""curate.workspace.model — workspace ontology

Defines containers (root / folder / file) and scoped facts.

Core principles:
- folders and files are NOT scopes
- scopes come only from Curate core
- hierarchy is encoded purely in NodeId tuples
- compilation policy lives on FileUnit, not in the workspace
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple, Mapping, Optional

NodeId = Tuple[int, ...]

# fundrar på om man ens behöver skilja mellan file och folder, kanske ändå då 
# file innehåller scopes och folder innehåller andra noder som i sig kan vara folders eller files
# här är kanske en stor skillnad, dvs att en folder kan innehålla andra folders
# medan en file inte kan innehålla andra files, dock kan files innehålla "länkar"
# till andra files via ex import eller #INCLUDE, på så vis har dem en relation
# på sätt och vis hierarkisk då det annars skulle leda till cirkulära beroenden
# det liknar alltså hela modellens ide kring decendents och ancestors etc.
# funderar även på varför man behöver ha "ROOT" då det automatiskt är första 
# elementet i Tuple[int, ...], elelr om då vald fokus punkt som cursor position
# låser root till dess Tuple[int, ...] address. 
# känns som workspace borde gå att göra mycket mindre då detta egentligen är 
# samma som scopesets?
# denna ska ju även, i min vission, kunna leta rekursivt från cwd och uppåt för
# att skapa addresser med samma hierarki som då kan gå från:
# project/folder/file/class/method/if_statement, där det kan finnas flera olika
# project i samma workspace och i varje project kan det finnas flera olika folders
# som i sig kan innehålla flera olika files eller andra folders med files etc.
class NodeKind(str, Enum):
    ROOT = "root"
    FOLDER = "folder"
    FILE = "file"


@dataclass(frozen=True, slots=True)
class FileUnit:
    """
    A compilation unit for the workspace.

    A FileUnit describes *what* is compiled and *how*.

    - path      : filesystem identity
    - source    : immutable source text
    - language  : syntax / grammar selection
    - producer  : scope production backend

    The workspace never infers or mutates these values.
    """

    path: Path
    source: str
    language: Optional[str] = None
    producer: str = "treesitter"


@dataclass(frozen=True, slots=True)
class WorkspaceNode:
    """
    A container node in the workspace hierarchy.

    Nodes represent:
    - the workspace root
    - folders
    - files

    They are structural only and never carry scopes.
    """

    id: NodeId
    label: NodeKind
    name: str
    path: Path


@dataclass(frozen=True, slots=True)
class WorkspaceScope:
    """
    Curate Scope lifted into workspace hierarchy.

    Notes:
    - id is a workspace NodeId (file_id + scope.address)
    - file_id always refers to a FILE node
    """

    id: NodeId
    label: str
    start: int
    end: int
    file_id: NodeId


@dataclass(frozen=True, slots=True)
class Workspace:
    """
    Immutable workspace.

    Invariants:
    - root.id == (0,)
    - root.label == NodeKind.ROOT
    - every WorkspaceScope.file_id exists and is FILE
    - ids are deterministic for identical inputs
    """

    root: WorkspaceNode
    nodes: Mapping[NodeId, WorkspaceNode]
    path_to_id: Mapping[Path, NodeId]
    scopes: Tuple[WorkspaceScope, ...]
