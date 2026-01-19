"""curate.workspace — project / file / folder adapter around Curate core

This layer:
- introduces folders and files as structural containers
- resolves language per file
- delegates syntax extraction to Curate core
- produces a unified laminar hierarchy:

    workspace → folders → files → scopes

Non-goals:
- no semantic interpretation
- no text slicing
- no cursor logic
- no policy or filtering
"""

from .model import (
    NodeId,
    NodeKind,
    FileUnit,
    WorkspaceNode,
    WorkspaceScope,
    Workspace,
)

from .language import (
    LanguageResolver,
    default_language_resolver,
)

from .build import build_workspace

from .query import (
    node_by_path,
    parent_of,
    children_of,
    scopes_in_file,
    scopes_under,
)

__all__ = [
    "NodeId",
    "NodeKind",
    "FileUnit",
    "WorkspaceNode",
    "WorkspaceScope",
    "Workspace",
    "LanguageResolver",
    "default_language_resolver",
    "build_workspace",
    "node_by_path",
    "parent_of",
    "children_of",
    "scopes_in_file",
    "scopes_under",
]
