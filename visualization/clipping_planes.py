import nibabel as nib
import pyvista as pv

def visualize_clipping_planes(nifti_path):
    print(f"[Clipping Planes] Visualizing NIfTI file: {nifti_path}")

    img = nib.load(nifti_path)
    data = img.get_fdata()

    grid = pv.wrap(data)
    contour = grid.contour([data.max() / 2])

    plotter = pv.Plotter()
    plotter.add_mesh(contour, color="lightblue")

    # Enable an interactive clipping plane
    plotter.enable_clipping_plane(widget_color="orange")

    plotter.add_text("Clipping Planes Active", position="upper_left", font_size=12)
    return plotter
