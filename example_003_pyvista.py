import pyvista as pv

reader = pv.get_reader("results/modes.pvd")
print(f"Number of time points: {reader.number_time_points}")

for t in range(reader.number_time_points):
    reader.set_active_time_point(t)
    multiblock = reader.read()
    grid = multiblock[0]  # ← extract first block
    print(f"Timestep {t}: {grid.array_names}")

    warped = grid.warp_by_vector("displacement", factor=0.1)

    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(warped, scalars="displacement",
                     component=None,
                     cmap="coolwarm", show_edges=True)
    plotter.view_isometric()
    plotter.screenshot(f"results/mode_{t}.png")
    plotter.close()
    print(f"Saved results/mode_{t}.png")
