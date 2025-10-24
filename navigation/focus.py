import vtk
import numpy as np
from PyQt5.QtCore import QTimer

class FlythroughNavigator:
    def __init__(self, renderer=None):
        self.renderer = renderer
        self.camera = None if renderer is None else renderer.GetActiveCamera()
        self.path_points = []
        self.current_point = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        
    def set_path(self, path_points):
        """Set the camera path points
        
        Args:
            path_points: List of (x,y,z) points defining the camera path
        """
        self.path_points = np.array(path_points)
        self.current_point = 0
        
    def start_flythrough(self, speed=1.0):
        """Start the flythrough animation
        
        Args:
            speed: Animation speed in points per second
        """
        if self.renderer is None or len(self.path_points) < 2:
            return
            
        self.timer.start(int(1000/speed))
        
    def stop_flythrough(self):
        """Stop the flythrough animation"""
        self.timer.stop()
        
    def update_camera(self):
        """Update camera position along the path"""
        if self.current_point >= len(self.path_points) - 1:
            self.stop_flythrough()
            return
            
        # Get current and next points
        current = self.path_points[self.current_point]
        next_point = self.path_points[self.current_point + 1]
        
        # Update camera position
        self.camera.SetPosition(current[0], current[1], current[2])
        self.camera.SetFocalPoint(next_point[0], next_point[1], next_point[2])
        self.camera.SetViewUp(0, 1, 0)
        
        # Update renderer
        self.renderer.ResetCameraClippingRange()
        self.renderer.GetRenderWindow().Render()
        
        self.current_point += 1
        
    def set_renderer(self, renderer):
        """Set the VTK renderer
        
        Args:
            renderer: vtkRenderer instance
        """
        self.renderer = renderer
        self.camera = renderer.GetActiveCamera()

class FocusController:
    def __init__(self, renderer=None):
        self.renderer = renderer
        self.actors = {}
        self.focused_actor = None
        
    def set_renderer(self, renderer):
        """Set the VTK renderer
        
        Args:
            renderer: vtkRenderer instance
        """
        self.renderer = renderer
        self.actors = {actor: actor.GetProperty().GetOpacity() 
                      for actor in renderer.GetActors()}
    
    def focus_on(self, target_actor, opacity=0.2):
        """Focus on a specific actor by reducing others' opacity
        
        Args:
            target_actor: vtkActor to focus on
            opacity: float opacity for non-focused actors (0-1)
        """
        if self.renderer is None:
            return
            
        # Store original opacities if not already stored
        if not self.actors:
            self.actors = {actor: actor.GetProperty().GetOpacity() 
                         for actor in self.renderer.GetActors()}
        
        # Set opacity for all actors
        for actor in self.renderer.GetActors():
            if actor != target_actor:
                actor.GetProperty().SetOpacity(opacity)
            else:
                actor.GetProperty().SetOpacity(1.0)
                
        self.focused_actor = target_actor
        self.renderer.GetRenderWindow().Render()
    
    def reset_focus(self):
        """Reset all actors to their original opacity"""
        if self.renderer is None:
            return
            
        for actor, opacity in self.actors.items():
            actor.GetProperty().SetOpacity(opacity)
            
        self.focused_actor = None
        self.renderer.GetRenderWindow().Render()