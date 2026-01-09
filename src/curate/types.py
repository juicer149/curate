from __future__ import annotations

from typing import Literal

Range = tuple[int, int]        # 1-based inclusive
Role = Literal["code", "doc"]
FoldMode = Literal["self", "children"]
