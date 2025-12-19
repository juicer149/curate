"""
Curate input contract.

Place in pipeline:
- An adapter (CLI/editor) constructs Config for a single request
- engine.fold(cfg) consumes it unchanged
- the selected backend uses the values to compute fold ranges

Config is immutable because folding is a pure computation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """
    Complete description of a folding request.

    Fields:
    - file_type:
        Language identifier used for backend selection (e.g. "python").

    - content:
        Full source text (immutable).

    - cursor:
        1-based cursor line.

    - level:
        Structural "zoom-out" control.
        Semantics are backend-defined, but level=0 is mandatory.

    - fold_children:
        View selector (f vs F):
        - True  => fold bodies of the target's children (keep their headers)
        - False => fold the body of the target itself (keep its header)
    """

    file_type: str
    content: str
    cursor: int
    level: int = 0
    fold_children: bool = True
