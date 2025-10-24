import nibabel as nib
import pyvista as pv
import numpy as np

def visualize_surface_rendering(nifti_path):
    print(f"[Surface Rendering] Visualizing NIfTI file: {nifti_path}")

    img = nib.load(nifti_path)
    data = img.get_fdata()

    # Convert to PyVista grid and extract iso-surface
    grid = pv.wrap(data)
    contour = grid.contour([data.max() / 2])

    # Create plotter but DO NOT show yet
    plotter = pv.Plotter()
    plotter.add_mesh(contour, color="lightblue")
    plotter.add_text("Surface Rendering", position="upper_left", font_size=12)

    return plotter  # ✅ Return instead of show()
