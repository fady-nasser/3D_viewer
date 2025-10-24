import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from io_utils import load_nifti, load_csv  # Changed from io to io_utils
from visualization import SurfaceRenderer
from navigation import FlythroughNavigator

class Viewer3DApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
    
    def run(self):
        self.main_window.show()
        return self.app.exec_()

if __name__ == '__main__':
    viewer = Viewer3DApp()
    sys.exit(viewer.run())