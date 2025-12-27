# tests/example_model.py
"""
Example Python source used for folding tests.

This file is intentionally verbose and structured to exercise:
- module docstring
- multiple classes
- class docstrings
- method docstrings
- top-level functions

It is not part of Curate itself.
"""

from dataclasses import dataclass


@dataclass
class Example:
    """
    A example class with structured data.

    Attributes:
        name (str): The name of the example.
        value (int): The value associated with the example.
    """

    def __init__(self, name: str, value: int):
        """
        Initializes the Example class with a name and value.

        Args:
            name (str): The name of the example.
            value (int): The value associated with the example.
        """
        self.name = name
        self.value = value

    def display(self) -> str:
        """
        Returns a string representation of the example.

        Returns:
            str: A formatted string with the name and value.
        """
        return f"Example Name: {self.name}, Example Value: {self.value}"


class ExampleForTwoClassesInFile:
    """
    A second example class in the same file.

    Attributes:
        description (str): A description of the example.
        amount (float): An amount associated with the example.
    """

    def __init__(self, description: str, amount: float):
        """
        Initializes the ExampleForTwoClassesInFile class with a description and amount.

        Args:
            description (str): A description of the example.
            amount (float): An amount associated with the example.
        """
        self.description = description
        self.amount = amount

    def summarize(self) -> str:
        """
        Returns a summary string of the example.

        Returns:
            str: A formatted string with the description and amount.
        """
        return f"Description: {self.description}, Amount: {self.amount}"


def example_function() -> str:
    """
    A simple example function that returns a greeting message.

    Returns:
        str: A greeting message.
    """
    return "Hello from example_function!"
