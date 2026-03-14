
import numpy as np

from mpi4py import MPI
from dolfinx.io import VTKFile
from dolfinx import fem
from dolfinx import la
from dolfinx import io
from dolfinx.fem.petsc import assemble_matrix

import ufl
from basix.ufl import element

from petsc4py import PETSc
from slepc4py import SLEPc


with io.XDMFFile(MPI.COMM_WORLD, "results/plate.xdmf", "r") as xdmf:
    mesh = xdmf.read_mesh(name="Grid")

gdim = mesh.geometry.dim

El = element("Lagrange", mesh.basix_cell(), 1, shape=(gdim,) )
V = fem.functionspace(mesh, El)

E = 2.0e11       # Young's modulus (Pa)
nu = 0.3         # Poisson's ratio
rho = 7800       # density (kg/m³)

lambda_ = E*nu/((1+nu)*(1-2*nu))
mu = E/(2*(1+nu))

u = ufl.TrialFunction(V)
v = ufl.TestFunction(V)



def epsilon(w):
    return ufl.sym(ufl.grad(w))

def sigma(w):
    return lambda_*ufl.tr(epsilon(w))*ufl.Identity(gdim) + 2*mu*epsilon(w)

def clamped_boundary(x):
    x_min = mesh.geometry.x[:, 0].min()
    return np.isclose(x[0], x_min, atol=1e-10)

bc_dofs = fem.locate_dofs_geometrical(V, clamped_boundary)
zero_vec = fem.Constant(mesh, PETSc.ScalarType((0.0, 0.0, 0.0)))
bc = fem.dirichletbc(zero_vec, bc_dofs, V)
bcs = [bc]

a_form = fem.form(ufl.inner(sigma(u), epsilon(v))*ufl.dx)      # bilinear form → stiffness
m_form = fem.form(ufl.inner(u, v)*ufl.dx)                      # mass form → mass

A = assemble_matrix(a_form, bcs=bcs)
M = assemble_matrix(m_form, bcs=bcs)

A.assemble()
M.assemble()

print(f"A size: {A.getSize()}, norm: {A.norm()}")
print(f"M size: {M.getSize()}, norm: {M.norm()}")

eigensolver = SLEPc.EPS().create(MPI.COMM_WORLD)
eigensolver.setOperators(A, M)
eigensolver.setProblemType(SLEPc.EPS.ProblemType.GHEP)

st = eigensolver.getST()
st.setType(SLEPc.ST.Type.SINVERT)
st.setShift(1e6)  # tune: sqrt(1e6)/(2π) ≈ 159 Hz — adjust for your plate size

eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.TARGET_MAGNITUDE)
eigensolver.setTarget(1e6)
eigensolver.setTolerances(tol=1e-8, max_it=1000)
eigensolver.setDimensions(nev=100, ncv=200)
eigensolver.solve()

n_converged = eigensolver.getConverged()
print(f"Converged: {n_converged} eigenpairs")

vr = A.createVecRight()
vi = A.createVecRight()

for i in range(n_converged):
    lam = eigensolver.getEigenpair(i, vr, vi)
    if lam.real < 0:
        continue
    freq_hz = np.sqrt(lam.real) / (2 * np.pi)
    if freq_hz < 1.0:
        continue
    print(f"Mode {i+1}: λ = {lam.real:.4e}, f = {freq_hz:.2f} Hz")

    mode = fem.Function(V)
    mode.x.array[:] = vr.array
    mode.x.scatter_forward()


mode_out = fem.Function(V, name="displacement")

with VTKFile(MPI.COMM_WORLD, "results/modes.pvd", "w") as vtk:
    for i in range(n_converged):
        lam = eigensolver.getEigenpair(i, vr, vi)
        if lam.real < 0:
            continue
        freq_hz = np.sqrt(lam.real) / (2 * np.pi)
        if freq_hz < 1.0:
            continue
        mode = fem.Function(V)
        # Each process fills its own local slice
        local_size = V.dofmap.index_map.size_local * V.dofmap.index_map_bs
        mode.x.array[:local_size] = vr.array[:local_size]
        mode.x.scatter_forward()
        mode_out.interpolate(mode)
        vtk.write_function(mode_out, float(i))
