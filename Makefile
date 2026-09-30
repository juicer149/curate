# ============================================================
# Curate — minimal developer Makefile
# ============================================================

.PHONY: help venv install test clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "Curate — developer commands"
	@echo ""
	@echo "  make venv      Create virtual environment"
	@echo "  make install   Install project in editable mode (dev extras)"
	@echo "  make test      Run pytest suite"
	@echo "  make clean     Remove caches and build artifacts"
	@echo ""

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv
	$(PIP) install -e ".[dev]"

# ------------------------------------------------------------
# Testing
# ------------------------------------------------------------

test:
	$(PYTEST)

# ------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.coverage' -exec rm -rf {} +
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
