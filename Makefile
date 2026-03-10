.ONESHELL:
SHELL := /bin/bash

PIXISH := $(HOME)/.pixi

help:
	@echo "install_pixi  -  installs pixi if ~/.pixi is not found"
	@echo "  quickstart  -  initialises pixi, installs dependencies, runs minimal_example.py"
	@echo "   uninstall  -  removes installed files to allow starting from scratch"

pixi_install:
	@if [ ! -d "$(PIXISH)" ]; then \
		echo "Installing pixi..."; \
		curl -fsSL https://pixi.sh/install.sh | bash; \
	else \
		echo "Pixi already installed."; \
	fi

uv_install:
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "uv already installed."; \
	fi

quickstart: pixi_install uv_install
	set -e
	pixi run uv pip install -e . --system --no-deps
	pixi run python3 -c "import dolfinx; print(dolfinx.__version__)"
	@echo "dolfinx is installed..."
	pixi run mpirun -n 4 python3 minimal_example.py
	@echo "Everything seems to have run successfully!"

uninstall:
	@echo "Removing pixi environment and caches..."
	rm -rf .pixi
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +

