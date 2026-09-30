"""
Pytest configuration for Curate.

Defines shared markers and global test configuration.
"""

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "treesitter: tests that require tree-sitter and language bindings",
    )
