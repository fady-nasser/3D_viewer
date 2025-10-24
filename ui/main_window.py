from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QAction,
    QFileDialog, QApplication
)
from PyQt5.QtCore import Qt
from visualization import SurfaceRenderer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Viewer")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create surface renderer
        self.renderer = SurfaceRenderer(self)
        self.layout.addWidget(self.renderer.get_widget())
        
        # Setup UI components
        self.create_menu_bar()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)