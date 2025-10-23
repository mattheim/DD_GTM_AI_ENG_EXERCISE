PYTHON ?= python3
VENV_DIR := .venv

# Cross‑platform virtualenv python path
ifeq ($(OS),Windows_NT)
  VENV_PY := $(VENV_DIR)/Scripts/python.exe
else
  VENV_PY := $(VENV_DIR)/bin/python
endif

# Minimal, beginner-friendly targets

.PHONY: venv
venv:
	@# Create venv only if missing
	@if [ -x "$(VENV_PY)" ]; then \
		echo "Using existing venv: $(VENV_DIR)"; \
	else \
		echo "Creating venv at $(VENV_DIR)"; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

.PHONY: install
install: venv
	$(VENV_PY) -m pip install -U pip
	$(VENV_PY) -m pip install -r requirements.txt

.PHONY: seed
seed: install
	$(VENV_PY) seed.py $(SEED_ARGS)

.PHONY: run
run: install
	$(VENV_PY) main.py

.PHONY: setup
setup: seed
	@echo "Setup complete. Seeded CSV at in/speakers.csv"
