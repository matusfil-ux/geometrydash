.PHONY: all
.DEFAULT: help
all: help
PKG_MANAGER ?= uv

ifeq ($(PKG_MANAGER),poetry)
	RUN_CMD := poetry run --
	INSTALL_CMD := poetry install --with dev --with test --with docs
	PUBLISH_CMD := poetry publish --repository msd-dev
else ifeq ($(PKG_MANAGER),uv)
	RUN_CMD := uv run --
	INSTALL_CMD := uv sync --group dev --group test --group docs
	PUBLISH_CMD := uv publish --index msd-dev
else
	$(error PKG_MANAGER must be either 'poetry' or 'uv')
endif

# Newline hack for error messages
define n


endef

.PHONY: develop
## Install development environment
develop:
	$(INSTALL_CMD)

.PHONY: format
## Format code using ruff
format:
	$(RUN_CMD) ruff format .
	$(RUN_CMD) ruff check --fix .

.PHONY: check_format
## Check code formatting without making changes
check_format:
	$(RUN_CMD) ruff format --diff .
	$(RUN_CMD) ruff check --diff --exit-zero .
	$(RUN_CMD) pyright

.PHONY: test
## Run tests
test:
	$(RUN_CMD) pytest

.PHONY: build
## Build package
build:
	python -m build

.PHONY: build_docs
## Build documentation from 'docsrc'
build_docs:
	$(RUN_CMD) docsrc/build.sh

.PHONY: publish
## Publish package to 'msd-dev' repository
publish:
	$(PUBLISH_CMD)

.PHONY: check
## Check code formatting and run tests
check: check_format test

.PHONY: dist_clean
## Remove distribution files
dist_clean:
	rm -rf dist

.PHONY: clean
## Remove all build artifacts and caches
clean: dist_clean
	rm -rf .mypy_cache .pytest_cache .ruff_cache docs

.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| less $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
