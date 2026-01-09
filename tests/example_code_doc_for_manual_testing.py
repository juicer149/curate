"""
Manual folding playground for Curate.

This file is intentionally large and verbose.
Its sole purpose is to exercise folding behavior.

Things to try manually:
- fold self vs children
- fold at different cursor levels
- folding decorators
- folding nested blocks
- folding docstrings vs code
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


# ─────────────────────────────────────────────────────────────
# Top-level utility functions
# ─────────────────────────────────────────────────────────────

def simple_function():
    """One-line docstring."""
    x = 1
    y = 2
    return x + y


def documented_function(a: int, b: int) -> int:
    """
    Add two numbers.

    This function exists mainly to test
    docstring folding behavior.

    Args:
        a (int): first number
        b (int): second number

    Returns:
        int: sum of a and b
    """
    result = a + b

    if result > 10:
        print("Large number")
    else:
        print("Small number")

    return result


def nested_blocks(n: int) -> int:
    """
    Function with multiple nested blocks.
    """
    total = 0

    for i in range(n):
        if i % 2 == 0:
            total += i
        else:
            total -= i

    try:
        while total < 100:
            total += 10
    except Exception as e:
        print("Error:", e)
    finally:
        print("Done looping")

    return total


# ─────────────────────────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────────────────────────

def debug(func):
    """
    Simple decorator that prints calls.
    """
    def wrapper(*args, **kwargs):
        print("Calling", func.__name__)
        return func(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────
# Classes
# ─────────────────────────────────────────────────────────────

@dataclass
class User:
    """
    Represents a user in the system.

    Attributes:
        name (str)
        age (int)
    """

    name: str
    age: int

    def is_adult(self) -> bool:
        """Return True if user is an adult."""
        return self.age >= 18

    def greet(self) -> str:
        """
        Create a greeting string.
        """
        if self.is_adult():
            return f"Hello {self.name}, welcome!"
        else:
            return f"Hi {self.name}!"


class Manager(User):
    """
    A user with management responsibilities.
    """

    def __init__(self, name: str, age: int, team: Optional[list[str]] = None):
        """
        Initialize manager.

        Args:
            name (str)
            age (int)
            team (list[str] | None)
        """
        super().__init__(name, age)
        self.team = team or []

    def add_member(self, member: str) -> None:
        self.team.append(member)

    def summary(self) -> str:
        """
        Return a summary of the manager.
        """
        return f"{self.name} manages {len(self.team)} people"


# ─────────────────────────────────────────────────────────────
# Nested classes
# ─────────────────────────────────────────────────────────────

class Outer:
    """
    Outer class to test nested scopes.
    """

    class Inner:
        """
        Inner class nested inside Outer.
        """

        def inner_method(self):
            """
            Method inside inner class.
            """
            print("Inner method")

    def outer_method(self):
        """
        Method in outer class.
        """
        inner = self.Inner()
        inner.inner_method()


# ─────────────────────────────────────────────────────────────
# More complex control-flow examples
# ─────────────────────────────────────────────────────────────

@debug
def complex_flow(items: Iterable[int]) -> int:
    """
    Function combining decorators, loops, and branches.
    """
    acc = 0

    for item in items:
        if item < 0:
            continue

        if item == 0:
            break

        acc += item

    match acc:
        case 0:
            print("Zero")
        case 1 | 2 | 3:
            print("Small")
        case _:
            print("Large")

    return acc


# ─────────────────────────────────────────────────────────────
# Edge cases
# ─────────────────────────────────────────────────────────────

def empty_body():
    """
    Function with a pass statement.
    """
    pass


def try_only():
    try:
        x = 1 / 0
    except ZeroDivisionError:
        print("Division by zero")


def deeply_nested():
    if True:
        if True:
            if True:
                if True:
                    print("Very deep")


# End of file
