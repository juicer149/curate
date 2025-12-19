"""
Shared type definitions.

Place in pipeline:
- Used across engine, backends, and adapters
- Defines stable, language-agnostic value types

This module exists to avoid type duplication and
to make cross-layer contracts explicit.
"""

from typing import Tuple

# Inclusive, 1-based line range
Range = Tuple[int, int]
