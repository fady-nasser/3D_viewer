import vtk
from PyQt5.QtWidgets import QVBoxLayout, QFrame
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class SurfaceRenderer:
    def __init__(self, parent=None):
        self.frame = QFrame()
        self.layout = QVBoxLayout()
        
        # Create VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self.frame)
        self.layout.addWidget(self.vtk_widget)
        self.frame.setLayout(self.layout)
        
        # Create renderer and render window
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        
        # Set background color
        self.renderer.SetBackground(0.1, 0.1, 0.1)
        
        # Initialize interactor and start
        self.interactor.Initialize()
        self.interactor.Start()
        
    def render_volume(self, volume_data, threshold=0.5):
        """Render volume data as a surface
        
        Args:
            volume_data: 3D numpy array containing the volume data
            threshold: float value for surface thresholding (default: 0.5)
        """
        # Convert numpy array to VTK data
        vtk_data = vtk.vtkImageData()
        vtk_data.SetDimensions(volume_data.shape)
        vtk_data.AllocateScalars(vtk.VTK_FLOAT, 1)
        
        for i in range(volume_data.shape[0]):
            for j in range(volume_data.shape[1]):
                for k in range(volume_data.shape[2]):
                    vtk_data.SetScalarComponentFromFloat(i, j, k, 0, volume_data[i,j,k])
        
        # Create surface using marching cubes
        surface = vtk.vtkMarchingCubes()
        surface.SetInputData(vtk_data)
        surface.SetValue(0, threshold)
        
        # Create mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(surface.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 1.0, 1.0)
        
        # Add actor to renderer
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
    def get_widget(self):
        """Returns the widget containing the visualization"""
        return self.frame
    
    def clear(self):
        """Clear all actors from the renderer"""
        self.renderer.RemoveAllViewProps()
        self.vtk_widget.GetRenderWindow().Render()