.DEFAULT_GOAL := help

PYTHON := .venv/bin/python
PIP    := .venv/bin/pip

.PHONY: help install validate test lint clean

help:
	@echo "devexnet targets:"
	@echo "  install   Create .venv and install dependencies"
	@echo "  validate  Run all validators (pre-commit, LOOM schema, shellcheck)"
	@echo "  test      Run test suite with coverage"
	@echo "  lint      Run ruff linter"
	@echo "  clean     Remove .venv, __pycache__, build artifacts"

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	pre-commit install

validate:
	pre-commit run --all-files
	bash scripts/validate_loomreed_light.sh
	shellcheck scripts/*.sh

test:
	$(PYTHON) -m pytest src/ tests/ --cov=src --cov-report=term-missing \
		--cov-fail-under=80

lint:
	$(PYTHON) -m ruff check src/

clean:
	rm -rf .venv __pycache__ dist build *.egg-info .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
