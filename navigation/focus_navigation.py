import pyvista as pv
import vtk

def start_focus_navigation(plotter=None):
    """
    Add Focus Navigation controls via keyboard to any PyVista plotter.
    Controls:
        Arrow keys: Rotate view
        +/-: Zoom in/out
        R: Reset view
    """
    print("[Navigation] Focus Navigation started")

    if plotter is None:
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="lightblue")
        plotter.add_text("Demo Mode", position="upper_left", font_size=12)

    def rotate_left():
        plotter.camera.azimuth += 10
        plotter.render()

    def rotate_right():
        plotter.camera.azimuth -= 10
        plotter.render()

    def rotate_up():
        plotter.camera.elevation += 10
        plotter.render()

    def rotate_down():
        plotter.camera.elevation -= 10
        plotter.render()

    def zoom_in():
        plotter.camera.zoom(1.2)
        plotter.render()

    def zoom_out():
        plotter.camera.zoom(0.8)
        plotter.render()

    def reset_view():
        plotter.camera_position = 'iso'
        plotter.reset_camera()
        plotter.render()

    # Keyboard bindings
    plotter.add_key_event("Left", rotate_left)
    plotter.add_key_event("Right", rotate_right)
    plotter.add_key_event("Up", rotate_up)
    plotter.add_key_event("Down", rotate_down)
    plotter.add_key_event("plus", zoom_in)
    plotter.add_key_event("minus", zoom_out)
    plotter.add_key_event("r", reset_view)

    # Add instructions text
    plotter.add_text(
        "Focus Navigation Controls:\n"
        "←↑↓→: Rotate camera\n"
        "+/-: Zoom in/out\n"
        "R: Reset view",
        position="upper_left",
        font_size=12
    )

    # Enable trackball camera style for mouse interaction
    plotter.enable_trackball_style()
    
    # Show the plotter
    plotter.show()
