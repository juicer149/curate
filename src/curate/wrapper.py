from __future__ import annotations

"""
Wrapper rules.

A wrapper is a node that should not create a scope itself, but whose
start line should be included in the header of a child scope.

Example:
  Python decorators wrap class/function definitions.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WrapperRule:
    """
    Declarative wrapper forwarding rule.

    wrapper_type:
      Tree-sitter node type acting as a wrapper.

    target_types:
      Child node types eligible to receive the wrapper's start line.
    """

    wrapper_type: str
    target_types: tuple[str, ...]
