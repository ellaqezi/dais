.DEFAULT_GOAL := help

PYTHON     := .venv/bin/python
PIP        := .venv/bin/pip
PRECOMMIT  := .venv/bin/pre-commit

MIN_PYTHON_MINOR := 11

.PHONY: help check-prereqs install validate test lint clean

help:
	@echo "dex targets:"
	@echo "  install      Create .venv and install all dependencies (runs check-prereqs first)"
	@echo "  validate     Run all validators: pre-commit hooks (incl. shellcheck), LOOM schema"
	@echo "  test         Run test suite with coverage"
	@echo "  lint         Run ruff linter"
	@echo "  clean        Remove .venv, __pycache__, build artifacts"
	@echo ""
	@echo "After install, activate the venv to use 'dex' on PATH:"
	@echo "  source .venv/bin/activate"
	@echo "  (or invoke directly: .venv/bin/dex)"

check-prereqs:
	@command -v python3 >/dev/null 2>&1 || { \
		echo "ERROR: python3 not found. Install Python 3.11+ and add it to PATH."; exit 1; }
	@python3 -c "import sys; v=sys.version_info; \
		sys.exit(0 if v.minor >= $(MIN_PYTHON_MINOR) else 1)" || { \
		echo "ERROR: Python 3.$(MIN_PYTHON_MINOR)+ required. Found: $$(python3 --version)"; exit 1; }
	@command -v git >/dev/null 2>&1 || { \
		echo "ERROR: git not found. Install git before running make install."; exit 1; }
	@command -v shellcheck >/dev/null 2>&1 || { \
		echo "ERROR: shellcheck not found."; \
		echo "  macOS:  brew install shellcheck"; \
		echo "  Debian: apt-get install shellcheck"; \
		echo "  RHEL:   yum install ShellCheck"; \
		exit 1; }
	@echo "Prerequisites OK: $$(python3 --version), git $$(git --version | awk '{print $$3}'), shellcheck $$(shellcheck --version | awk 'NR==2{print $$2}')"

install: check-prereqs
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PRECOMMIT) install
	@echo ""
	@echo "Install complete. Activate the venv to use 'dex' on PATH:"
	@echo "  source .venv/bin/activate"
	@echo "  dex --help"
	@echo "Or invoke without activating: .venv/bin/dex --help"
	@echo "Run 'make validate' to verify the full setup."

validate:
	$(PRECOMMIT) run --all-files
	bash scripts/validate_loomreed_light.sh
	bash scripts/validate_adrs.sh
	bash scripts/validate_stubs.sh
	shellcheck scripts/*.sh

test:
	$(PYTHON) -m pytest src/ tests/ --cov=src --cov-report=term-missing \
		--cov-fail-under=80

lint:
	$(PYTHON) -m ruff check src/

clean:
	rm -rf .venv __pycache__ dist build *.egg-info .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
