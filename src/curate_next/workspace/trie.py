"""
curate.workspace.trie — deterministic path trie

Builds a tree of folders/files before assigning NodeIds.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


@dataclass
class TrieNode:
    name: str
    path: Path
    children: Dict[str, "TrieNode"] = field(default_factory=dict)
    is_file: bool = False
