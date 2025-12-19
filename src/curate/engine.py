"""
Curate folding orchestration.

Place in pipeline:
- Adapters (CLI/editor) build a Config (config.py)
- engine.fold(cfg) selects a backend (backend_factory.py)
- engine delegates folding to the backend
- engine normalizes ranges into the stable output contract

Engine responsibilities:
- backend dispatch (no language logic here)
- range normalization (final authority on output shape)

The engine does not interpret `level`.
Backends define level semantics, except the shared invariant:
- level == 0 targets the smallest structural scope containing the cursor.
"""

from .backend_factory import get_backend
from .config import Config
from .types import Range


def _normalize(ranges) -> tuple[Range, ...]:
    """
    Normalize backend-produced ranges into Curate's output contract.

    Rules:
    - sort by start line
    - merge overlapping or adjacent ranges
    - drop invalid ranges where start >= end

    Backends may return unsanitized ranges; the engine is the final authority.
    """
    rs = [(a, b) for a, b in ranges if a < b]
    if not rs:
        return ()

    rs.sort()
    out = [rs[0]]

    for a, b in rs[1:]:
        la, lb = out[-1]
        if a <= lb + 1:
            out[-1] = (la, max(lb, b))
        else:
            out.append((a, b))

    return tuple(out)


def fold(cfg: Config) -> tuple[Range, ...]:
    """
    Compute fold ranges for a single folding request.

    This function is pure:
    - no caching
    - no mutation
    - same input => same output
    """
    backend = get_backend(cfg.file_type)
    if backend is None:
        # Keep policy here if you prefer strictness:
        # raise ValueError(f"Unsupported file_type: {cfg.file_type}")
        return ()

    ranges = backend.fold(
        content=cfg.content,
        cursor=cfg.cursor,
        level=cfg.level,
        fold_children=cfg.fold_children,
    )
    return _normalize(ranges)
