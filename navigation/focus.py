def apply_focus(plotter, target_mesh):
    # Example: reduce opacity of other objects to focus on target
    for actor in plotter.actors.values():
        actor.GetProperty().SetOpacity(0.2)
    target_mesh.GetProperty().SetOpacity(1.0)
