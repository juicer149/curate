"""
CLI bootstrap.

Allows:
    python -m curate

All logic lives in cli.py.
"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
