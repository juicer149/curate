from __future__ import annotations

"""
Tree-sitter producer backend.

This package implements a Tree-sitter–based `Producer` for curate.
It converts source text into a `ScopeGraph` using a strictly layered design.

Responsibilities
----------------
- Tree-sitter is used ONLY for syntax parsing.
- No semantic decisions are hard-coded.
- No editor-specific logic exists here.
- All language behavior is expressed declaratively via LanguageRules.

Pipeline
--------
1. Parse source text into a Tree-sitter syntax tree.
2. Traverse the tree in a deterministic, language-agnostic way.
3. Interpret each node via NodePolicy and WrapperRule.
4. Produce a laminar ScopeGraph.

Adding a new language
---------------------
To add a new Tree-sitter language backend:

1. Install a Tree-sitter grammar package.
2. Define LanguageRules for the language:
   - scope node types
   - wrapper node types
   - default NOOP behavior
3. Register:
   - LanguageRules
   - a loader returning tree_sitter.Language
4. No traversal or engine code changes are required.

This package intentionally contains only Tree-sitter–specific code.
"""

from .producer import build_graph

__all__ = ["build_graph"]
