# Context-AI Development Makefile

.PHONY: help setup install install-dev clean dev-install test test-watch lint format type-check build publish

# Default target
help:
	@echo "Context-AI Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Setup:"
	@echo "  setup          Complete development setup (venv + deps)"
	@echo "  install        Install production dependencies"  
	@echo "  install-dev    Install development dependencies"
	@echo "  dev-install    Install in development mode (-e .)"
	@echo "  clean          Clean build artifacts and cache"
	@echo ""
	@echo "Development:"
	@echo "  test           Run all tests"
	@echo "  test-watch     Run tests in watch mode"  
	@echo "  lint           Run linting (flake8, mypy)"
	@echo "  format         Auto-format code (black, isort)"
	@echo "  type-check     Run type checking (mypy)"
	@echo ""
	@echo "Build & Release:"
	@echo "  build          Build package for distribution"
	@echo "  test-publish   Publish to TestPyPI (testing)"
	@echo "  alpha-publish  Publish alpha to TestPyPI (context-ai-alpha)"
	@echo "  publish        Publish to PyPI (production)"
	@echo "  test-install   Install from TestPyPI"
	@echo "  test-uninstall Uninstall context-ai"  
	@echo "  verify-install Verify installation works"
	@echo ""
	@echo "Usage Examples:"
	@echo "  make setup     # Setup new development environment"
	@echo "  make dev-install && make test-watch  # Development workflow"
	@echo "  make format lint type-check  # Pre-commit checks"

# Setup and Installation
setup:
	@echo "🚀 Setting up Context-AI development environment..."
	python -m venv venv
	@echo "📦 Virtual environment created"
	@echo "⚠️  Run 'source venv/bin/activate' to activate environment"
	@echo "⚠️  Then run 'make install-dev' to install dependencies"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

dev-install: install-dev

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Testing
test:
	pytest tests/ -v

test-watch:
	pytest-watch tests/ -- -v

# Code Quality
lint:
	@echo "🔍 Running linting..."
	flake8 src/ tests/
	mypy src/

format:
	@echo "✨ Formatting code..."
	autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --in-place --recursive src/ tests/
	black src/ tests/
	isort src/ tests/

type-check:
	@echo "🔎 Type checking..."
	mypy src/

# Build and Release
build: clean
	@echo "📦 Building package..."
	python -m build

publish: build
	@echo "🚀 Publishing to PyPI..."
	python -m twine upload dist/*

alpha-publish: clean
	@echo "🔄 Changing name to context-ai-alpha..."
	@cp pyproject.toml pyproject.toml.backup
	@sed 's/name = "context-ai"/name = "context-ai-alpha"/' pyproject.toml > pyproject.toml.tmp && mv pyproject.toml.tmp pyproject.toml
	@echo "📦 Building alpha package..."
	python -m build
	@echo "🚀 Publishing alpha to TestPyPI..."
	python -m twine upload --repository testpypi dist/*
	@echo "🔄 Restoring original name..."
	@mv pyproject.toml.backup pyproject.toml
	@echo "✅ Alpha published to TestPyPI successfully!"

alpha-install:
	@echo "🔍 Installing context-ai-alpha from TestPyPI with pipx..."
	pipx install --index-url https://test.pypi.org/simple/ context-ai-alpha --pre

alpha-uninstall:
	@echo "🗑️  Uninstalling context-ai-alpha..."
	pipx uninstall context-ai-alpha

verify:
	@echo "✅ Verifying installation..."
	context-ai --version
	context-ai --help

# Quick development workflow
dev: format lint test
	@echo "✅ Development checks passed!"
