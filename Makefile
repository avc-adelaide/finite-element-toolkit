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

pixi_init:
	@if [ ! -d '.pixi' ]; then \
		echo 'Initialising pixi project...'; \
		pixi init . && \
		pixi project channel add conda-forge && \
		pixi add fenics-dolfinx mpich; \
	else \
		echo 'Pixi project already initialised.'; \
	fi

quickstart: pixi_install pixi_init
	set -e
	pixi run uv pip install -e . --system
	pixi run python3 -c "import dolfinx; print(dolfinx.__version__)"
	@echo "dolfinx is installed..."
	pixi run mpirun -n 4 python3 minimal_example.py
	@echo "Everything seems to have run successfully!"

uninstall:
	@echo "Removing pixi environment and caches..."
	rm -rf .pixi
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +

