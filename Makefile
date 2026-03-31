.PHONY: all
.DEFAULT: help
all: help

.PHONY: develop
## Install development environment
develop:
	uv venv
	uv pip install -e .

.PHONY: run
## Run the game
run:
	uv run python -m geometrydash

.PHONY: build
## Build package
build:
	python -m build

.PHONY: clean
## Remove all build artifacts and caches
clean:
	rm -rf dist .mypy_cache .pytest_cache .ruff_cache build

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make develop   — create .venv and install dependencies"
	@echo "  make run       — run the game"
	@echo "  make build     — build the package"
	@echo "  make clean     — remove build artifacts"
