"""curate.workspace.query — structural queries over workspace
"""

from pathlib import Path
from typing import Tuple
from .model import Workspace, WorkspaceNode, WorkspaceScope, NodeId, NodeKind


def node_by_path(ws: Workspace, path: Path) -> WorkspaceNode | None:
    return ws.nodes.get(ws.path_to_id.get(path))


def parent_of(ws: Workspace, nid: NodeId) -> WorkspaceNode | None:
    if len(nid) <= 1:
        return None
    return ws.nodes.get(nid[:-1])


def children_of(ws: Workspace, nid: NodeId) -> Tuple[WorkspaceNode, ...]:
    plen = len(nid)
    return tuple(
        n for i, n in ws.nodes.items()
        if len(i) == plen + 1 and i[:-1] == nid
    )


def scopes_in_file(ws: Workspace, file: Path | NodeId) -> Tuple[WorkspaceScope, ...]:
    fid = ws.path_to_id.get(file) if isinstance(file, Path) else file
    return tuple(s for s in ws.scopes if s.file_id == fid)


def scopes_under(ws: Workspace, nid: NodeId) -> Tuple[WorkspaceScope, ...]:
    return tuple(s for s in ws.scopes if s.id[:len(nid)] == nid)
