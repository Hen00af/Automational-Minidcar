# mock/Makefile
.PHONY: run help clean

PYTHON := python3
PROJECT_ROOT := $(abspath ..)

help:
	@echo "Available targets: run, clean, help"

run:
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) -m mock

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

.DEFAULT_GOAL := run
