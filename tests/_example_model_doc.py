# tests/example_model.py
"""
Example Python source used for folding tests.

This file is intentionally verbose and structured to exercise:
- module docstring
- multiple classes
- class docstrings
- method docstrings
- top-level functions

It is not part of Curate itself. även denna ska i framtiden kunna folda endast sin docstring, ev med sektioner etc liknande markdown.
"""

from dataclasses import dataclass

# här borde f inte göra något alls, alternativ folda alla tomma rader i filen?


@dataclass # just nu så foldar denna allt i filen, men den borde egentligen ingå i klassen/funktionen som kommer därefters scope.
class Example: # om man här trycker på leader+f så foldas allt i denna klassen till sina
    # headers, dvs metodernas implementationer göms. Men om leader+F trycks så foldas
    # allt i klassen bort, inklusive metodernas headers, kvar är endast klassens namn.
    """
    A example class with structured data.

    Attributes:
        name (str): The name of the example.
        value (int): The value associated with the example.
    """

    def __init__(self, name: str, value: int): # samma gäller här, vid f så foldas endast 
        # denna metodens implementation bort, vid ff så ska den då in princip folda alla
        # dess syskon, men i logik så är det bara som en f på klassen, dvs på parentnoden.
        # säg att klassen har foldat med f och sedan befinner man sig här och trycker f,
        # då ska endast denna metodens implementation vecklas ut. I förlängningen så
        # ska den skilja mellan doc vs code, där doc alltid är synligt vid f om det utförs
        # via header, dvs funktionsnamn eller klassnamn. eller om man befinner sig i 
        # koden.
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
