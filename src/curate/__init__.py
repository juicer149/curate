"""
Curate — Structural Folding Engine.

Public API
----------
This package intentionally exposes a very small surface:

- fold(...)        : Compute fold ranges from source text and user intent

Everything else is internal and may change.

Philosophy
----------
Curate is built around a strict separation of concerns:

- Structure (facts):     what exists in the source text
- Language backends:     how structure is extracted for a given language
- Rules (policy):        how different structures should behave
- Evaluation (logic):    how intent is applied to facts using rules

This file marks the boundary between Curate as a library
and Curate as an implementation.
"""

from .engine import fold

__all__ = ["fold"]
