# act/Makefile
.PHONY: run help clean

# Python実行コマンド（必要に応じて python3 や venv の python に変更）
PYTHON := python3

# スクリプトのパス
SCRIPT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PROJECT_ROOT := $(abspath $(SCRIPT_DIR)..)
RUN_SCRIPT := $(SCRIPT_DIR)run.py

help:
	@echo "Available targets:"
	@echo "  run       - Run with real hardware (Raspberry Pi)"
	@echo "  help      - Show this help message"
	@echo "  clean     - Clean Python cache files"

run:
	@echo "=========================================="
	@echo "Running in REAL mode (requires Raspberry Pi)"
	@echo "=========================================="
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) $(RUN_SCRIPT)

clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Done."
