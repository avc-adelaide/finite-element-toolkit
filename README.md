# Finite Element Toolkit

This repository is a template and toolkit for undertaking finite element analysis using open source tools.
Currently the scope of the reposity covers:

* Defining geometry using `cadquery`
* Meshing using `gmsh`
* FEA using `dolphinx/fenicsx`
* Visualisation using `pyvista`

By cloning the repository and using the setup defined in the Makefile, you should be able to set up a working
finite element analysis simulation environment directly. This is performed using `pixi` and `uv` to define the
dependencies — as long as these tools are available for your system this workflow should ‘just work’.

## Documentation

Alongside the environment setup, a variety of examples and tests are provided to demonstrate functionality and
ensure the toolchains are working. Some didactic/formal documentation of the theory is also provided, but you
should take this with a grain of salt — I don't know anywhere near as much about the finite element method as
the people who have written these tools.

### Theory Document

A didactic introduction to the Finite Element Method (FEM) and its implementation in FEniCSx is available in the [`theory/`](theory/) folder.

**[View / Download PDF](https://avc-adelaide.github.io/finite-element-toolkit/fenics_theory.pdf)**

### Quarto Example

A hands-on walkthrough of a 1-D Poisson problem solved with pure NumPy (no FEM library required) is in the [`quarto/`](quarto/) folder.  The document includes code, maths, and a plot, and is rendered via [Quarto](https://quarto.org).

**[View Quarto document](https://avc-adelaide.github.io/finite-element-toolkit/quarto/)**


## Manual installation steps

I use a Mac, this will likely colour some of the steps (e.g. using `python3` instead of `python`).

1. Install pixi:
```
curl -fsSL https://pixi.sh/install.sh | bash
```

2. Initialise pixi:
```
pixi init .
```

3. Add fenicsx and other dependencies:
```
pixi install
```
These dependencies are defined in `pixi.toml`.

4. There are two ways to execute using `pixi`. The first is to enter `pixi shell` and use standard CLI methods within it.
The second approach, which is my preference, is to call `pixi run` as a prefix to the standard commands.
To start, install the necessary `uv` requirements:
```
pixi run uv pip install -e . --system
```
Add to these in the `pyproject.toml` file.

5. If all has gone well, check that everything is installed:
```
pixi run python3 -c "import dolfinx; print(dolfinx.__version__)"
```

6. Now you can run an example file:
```
pixi run mpirun -n 4 python3 minimal_example.py
```
(`minimal_example.py` is in the repo already)

The steps above are hard-coded into the `Makefile`:
```
make quickstart
```
You can then delete all of the installed files and start from fresh using
```
make uninstall
```
