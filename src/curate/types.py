"""
Core type aliases.

Why this exists
---------------
This module centralizes shared semantic types and keeps
stringly-typed logic out of the rest of the system.
"""

from typing import Literal, Tuple

Range = Tuple[int, int]
#new name
LineRange = Range

Role = Literal["code", "doc"]
FoldMode = Literal["self", "children"]
