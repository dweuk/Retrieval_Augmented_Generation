# PROJECT CONFIGURATION
AUTHOR=npapot
PROJECT_NAME=RAG

# COLORS
RED     = \033[0;31m
YELLOW  = \033[0;33m
GREEN   = \033[0;32m
CYAN    = \033[0;36m
RESET   = \033[0m

# MAIN VARIABLES
INTERPRETER			=	python


install:
	@echo "$(RED)╔════════════════════════════════════════════════════════════════╗"
	@echo "$(RED)║                                                                ║"
	@echo "$(RED)║  44  44    2222    Author:  $(GREEN)Made with pain by $(AUTHOR) $(RED)          ║"
	@echo "$(RED)║  44  44   22  22   Project: $(YELLOW)Best $(PROJECT_NAME) Ever $(RED)                     ║"
	@echo "$(RED)║  444444      22    Github:  $(CYAN)https://github.com/dweuk$      $(RED)      ║"
	@echo "$(RED)║      44     22                                                 ║"
	@echo "$(RED)║      44   222222                                               ║"
	@echo "$(RED)║                                                                ║"
	@echo "$(RED)╚════════════════════════════════════════════════════════════════╝"
	@echo
	@echo
	@echo
	@echo
	@echo "$(RED)══════════════════════════════════════════════════════════════════\n"
	@# ... (ASCII Art)
	@echo "$(YELLOW)[Installation]$(RESET) ➡️  Synchronizing uv\n"
	@echo "$(RED)══════════════════════════════════════════════════════════════════"
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "uv not found — installing via pipx\n"; \
		if ! command -v pipx >/dev/null 2>&1; then \
			python3 -m pip install --user pipx >/dev/null 2>&1 && python3 -m pipx ensurepath || true; \
		fi; \
		pipx install uv >/dev/null 2>&1 || python3 -m pip install --user uv >/dev/null 2>&1; \
	fi
	@uv sync

sync:
	uv sync

run:
	uv run python rag.py

ingest:
	uv run python rag.py ingest --data_directory "vllm-0.10.1"

debug: install
	uv run python -m pdb src

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	find . -type f -name "*.pyc" -delete

lint: install
	uv run python -m flake8 src
	uv run python -m mypy src

lint-strict: install
	uv run python -m flake8 src
	uv run python -m mypy --strict src

.PHONY: install run sync debug clean lint lint-strict