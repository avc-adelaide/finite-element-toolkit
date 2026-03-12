from dolfinx import mesh
from mpi4py import MPI

domain = mesh.create_unit_square(MPI.COMM_WORLD, 8, 8)
print(domain.topology.index_map(2).size_local)
