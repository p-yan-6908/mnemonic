.PHONY: help install test lint push clean

help:
	@echo "Mnemonic - Available Commands:"
	@echo "  make install    - Install package with dev dependencies"
	@echo "  make test       - Run test suite"
	@echo "  make lint       - Run linters"
	@echo "  make push       - Commit and push changes"
	@echo "  make clean      - Clean build artifacts"

install:
	pip install -e ".[dev,all]"

test:
	python3 -m pytest tests/ -v

test-cov:
	python3 -m pytest tests/ -v --cov=src/mnemonic --cov-report=html

lint:
	ruff check src/mnemonic/
	mypy src/mnemonic/

lint-fix:
	ruff check src/mnemonic/ --fix
	ruff format src/mnemonic/

push:
	@bash scripts/push.sh

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
