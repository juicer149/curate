"""
Curate — Structural Code Folding Engine (v1)

Curate operates purely on text and line numbers to compute foldable
ranges in structured source code.

It does not mutate source code.
It does not depend on any editor.

===============================================================================
Data Flow
===============================================================================

Adapter (CLI / editor)                          → cli.py
    ↓
Configuration object                            → config.py
    ↓
engine.fold                                    → engine.py
    ↓
backend_factory.get_backend                    → backend_factory.py
    ↓
backend.fold                                   → backends/*.py
    ↓
Node tree construction (backend-specific)      → node.py
    ↓
Range selection (backend-specific)
    ↓
engine normalization                           → engine.py
    ↓
Adapter applies folds                          → editor / CLI

===============================================================================
Public API
===============================================================================

- Config : input object describing a folding request
- fold   : compute fold ranges for a given Config

===============================================================================
Core Rule (v1)
===============================================================================

Every backend must implement level == 0.

Level 0 is defined as:
    Fold the smallest structural scope containing the cursor.

In v1:
- All structural nodes (code and docstrings) are treated uniformly.
- Semantic distinction between code and documentation is deferred.

===============================================================================
"""

from .config import Config
from .engine import fold

__all__ = ["Config", "fold"]
