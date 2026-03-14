import gmsh
import meshio

# Initialize Gmsh
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)

# Merge your STEP geometry
gmsh.merge("results/plate.step")

# Define the mesh size (can be tuned)
gmsh.model.mesh.generate(3)  # 3D mesh

# Write to MSH
gmsh.write("results/plate.msh")

# Finalize Gmsh
gmsh.finalize()



# Read Gmsh .msh
mesh = meshio.read("results/plate.msh")

# Separate cells and data for FEniCSx
tetra_cells = mesh.get_cells_type("tetra")
triangle_cells = mesh.get_cells_type("triangle")  # boundary

tetra_data = mesh.get_cell_data("gmsh:physical", "tetra") if "gmsh:physical" in mesh.cell_data else None
triangle_data = mesh.get_cell_data("gmsh:physical", "triangle") if "gmsh:physical" in mesh.cell_data else None

# Write the mesh to XDMF / HDF5
meshio.write("results/plate.xdmf",
    meshio.Mesh(points=mesh.points,
                cells={"tetra": tetra_cells},
                cell_data={"name_to_read":[tetra_data]} if tetra_data is not None else None)
)

meshio.write("results/plate_facet.xdmf",
    meshio.Mesh(points=mesh.points,
                cells={"triangle": triangle_cells},
                cell_data={"name_to_read":[triangle_data]} if triangle_data is not None else None)
)
