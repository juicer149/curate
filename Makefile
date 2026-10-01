# ============================================================
# Curate — minimal developer Makefile
# ============================================================

.PHONY: help venv install test test-nvim bench clean

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
	@echo "  make test-nvim Run the Neovim adapter tests (headless)"
	@echo "  make bench     Time producer, curation and chain at 100 to 100k lines"
	@echo "  make clean     Remove caches and build artifacts"
	@echo ""

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv
	$(PIP) install -e ".[dev,treesitter]"

# ------------------------------------------------------------
# Testing
# ------------------------------------------------------------

test:
	$(PYTEST) -q src/curate/tests

test-nvim:
	nvim --headless --clean -u NONE -c "luafile adapters/nvim/tests/zoom.lua"

# ------------------------------------------------------------
# Benchmark
# ------------------------------------------------------------

bench:
	$(PYTHON) scripts/bench_scaling.py

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
