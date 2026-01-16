# act/Makefile
.PHONY: mock_run run_mock run help clean

# Python実行コマンド（必要に応じて python3 や venv の python に変更）
PYTHON := python3

# スクリプトのパス
SCRIPT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PROJECT_ROOT := $(abspath $(SCRIPT_DIR)..)
MOCK_SCRIPT := $(SCRIPT_DIR)run_mock.py
RUN_SCRIPT := $(SCRIPT_DIR)run.py

help:
	@echo "Available targets:"
	@echo "  mock_run  - Run with mock implementations (for testing)"
	@echo "  run_mock  - Alias for mock_run"
	@echo "  run       - Run with real hardware (Raspberry Pi)"
	@echo "  help      - Show this help message"
	@echo "  clean     - Clean Python cache files"

mock_run run_mock:
	@echo "=========================================="
	@echo "Running in MOCK mode (no hardware required)"
	@echo "=========================================="
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) $(MOCK_SCRIPT)

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
