
import numpy as np
from mpi4py import MPI
import ufl, basix, dolfinx
from dolfinx import fem
import dolfinx.fem.petsc
from petsc4py import PETSc
from slepc4py import SLEPc

with dolfinx.io.XDMFFile(MPI.COMM_WORLD, "results/plate.xdmf", "r") as xdmf:
    mesh = xdmf.read_mesh(name="Grid")

poly_degree = 1
gdim = mesh.geometry.dim
El = basix.ufl.element( family="Lagrange",
                        cell=mesh.basix_cell(),
                        degree=poly_degree,
                        shape=(gdim,),
                      )
V = fem.functionspace(mesh, El)
u, v = ufl.TrialFunction(V), ufl.TestFunction(V)

E = 2.0e11       # Young's modulus (Pa)
nu = 0.3         # Poisson's ratio
rho = 7800       # density (kg/m³)
lame_param = E*nu/((1+nu)*(1-2*nu))
mu = E/(2*(1+nu))

def epsilon(w):
    return ufl.sym(ufl.grad(w))

def sigma(w):
    return lame_param * ufl.tr(epsilon(w)) * ufl.Identity(gdim) + 2 * mu * epsilon(w)

a = ufl.inner(sigma(u), epsilon(v)) * ufl.dx # bilinear form → stiffness
m = ufl.inner(u, v) * ufl.dx                 # mass form → mass

def clamped_boundary(x):
    x_min = mesh.geometry.x[:, 0].min()
    return np.isclose(x[0], x_min, atol=1e-10)

bc_dofs = fem.locate_dofs_geometrical(V, clamped_boundary)
zero_vec = fem.Constant(mesh, PETSc.ScalarType((0.0, 0.0, 0.0)))
bc = fem.dirichletbc(zero_vec, bc_dofs, V)

A = fem.petsc.assemble_matrix(fem.form(a), bcs=[bc])
M = fem.petsc.assemble_matrix(fem.form(m), bcs=[bc])

A.assemble()
M.assemble()

print(f"A size: {A.getSize()}, norm: {A.norm()}")
print(f"M size: {M.getSize()}, norm: {M.norm()}")

eigensolver = SLEPc.EPS().create(MPI.COMM_WORLD)
eigensolver.setOperators(A, M)
eigensolver.setProblemType(SLEPc.EPS.ProblemType.GHEP)

num_freqs = 100
freq_expect = 100 # Hz -- approximately where to start looking for resonance frequencies
lambda_tune = (freq_expect * 2 * np.pi)**2

st = eigensolver.getST()
st.setType(SLEPc.ST.Type.SINVERT)
st.setShift(lambda_tune)

eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.TARGET_MAGNITUDE)
eigensolver.setTarget(lambda_tune)
eigensolver.setTolerances(tol = 1e-8, max_it = 1000)
eigensolver.setDimensions(nev = num_freqs, ncv = 2 * num_freqs)
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

with dolfinx.io.VTKFile(MPI.COMM_WORLD, "results/modes.pvd", "w") as vtk:
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
