"""curate.workspace.build — workspace construction"""

from pathlib import Path
from typing import Iterable, Dict, List

from curate_next.compile import compile_scope_set

from .model import (
    FileUnit,
    Workspace,
    WorkspaceNode,
    WorkspaceScope,
    NodeKind,
    NodeId,
)
from .language import LanguageResolver, default_language_resolver
from .trie import TrieNode


def build_workspace(
    *,
    files: Iterable[FileUnit],
    root: Path | None = None,
    resolver: LanguageResolver | None = None,
) -> Workspace:
    resolver = resolver or default_language_resolver()
    units = list(files)

    if not units:
        root_path = (root or Path(".")).resolve()
        root_node = WorkspaceNode((0,), NodeKind.ROOT, root_path.name, root_path)
        return Workspace(root_node, {(0,): root_node}, {root_path: (0,)}, ())

    abs_units = [(u, u.path.expanduser().resolve()) for u in units]
    base = root.resolve() if root else _common_root([p for _, p in abs_units])

    trie = TrieNode(name=base.name, path=base)

    for _, path in abs_units:
        rel = path.relative_to(base)
        node = trie
        for part in rel.parts[:-1]:
            node = node.children.setdefault(
                part, TrieNode(part, node.path / part)
            )
        fname = rel.parts[-1]
        node.children.setdefault(
            fname, TrieNode(fname, path, is_file=True)
        ).is_file = True

    nodes: Dict[NodeId, WorkspaceNode] = {}
    path_to_id: Dict[Path, NodeId] = {}

    def assign(node: TrieNode, parent_id: NodeId) -> None:
        kind = (
            NodeKind.ROOT if parent_id == ()
            else NodeKind.FILE if node.is_file
            else NodeKind.FOLDER
        )

        nid = parent_id
        ws_node = WorkspaceNode(nid, kind, node.name, node.path)
        nodes[nid] = ws_node
        path_to_id[node.path] = nid

        children = sorted(
            node.children.values(),
            key=lambda n: (n.is_file, n.name),
        )

        for i, ch in enumerate(children):
            assign(ch, nid + (i,))

    assign(trie, (0,))

    scopes: List[WorkspaceScope] = []

    for unit, path in abs_units:
        file_id = path_to_id[path]
        lang = resolver.resolve(unit)
        scope_set = compile_scope_set(source=unit.source, language=lang)

        for s in scope_set:
            scopes.append(
                WorkspaceScope(
                    id=file_id + s.id,
                    kind=s.kind,
                    start=s.start,
                    end=s.end,
                    file_id=file_id,
                )
            )

    scopes.sort(key=lambda s: (s.file_id, s.start, -s.end, s.id))
    root_node = nodes[(0,)]
    return Workspace(root_node, nodes, path_to_id, tuple(scopes))


def _common_root(paths: List[Path]) -> Path:
    parts = paths[0].parts
    for p in paths[1:]:
        i = 0
        while i < len(parts) and i < len(p.parts) and parts[i] == p.parts[i]:
            i += 1
        parts = parts[:i]
    return Path(*parts).resolve()
