import pyvista as pv
import numpy as np

def surface_render(plotter, volume_data):
    """Basic surface rendering using PyVista threshold"""
    grid = pv.UniformGrid()
    grid.dimensions = volume_data.shape[::-1]
    grid.point_arrays["values"] = volume_data.flatten(order="F")
    surf = grid.threshold(0.5).extract_surface()
    plotter.add_mesh(surf, color="white", opacity=1.0)
    plotter.reset_camera()
