# curate/producers/__init__.py
from .registry import PRODUCERS, Producer, register

__all__ = ["PRODUCERS", "Producer", "register"]
