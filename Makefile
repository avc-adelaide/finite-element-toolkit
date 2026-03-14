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

reset:
	@echo "Removing pixi & uv environment and caches..."
	rm -rf .pixi
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +

example: example_000 example_001 example_002 example_003
	@echo "It actually worked (!)"

example_000:
	pixi run uv run example_000_cadquery.py

example_001:
	pixi run uv run example_001_gmsh.py

example_002:
	pixi run mpirun -n 1 python3 example_002_mesh_fenics.py

example_003:
	pixi run uv run example_003_pyvista.py
