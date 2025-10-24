from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QGroupBox, QRadioButton, QFileDialog, QTextEdit
)
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
import pyvista as pv
import sys
from io.load_nifti import load_nifti
from io.load_csv import load_csv
from visualization.surface_render import surface_render

SYSTEMS = ["Nervous", "Cardiovascular", "Musculoskeletal", "Mouth/Dental"]

VALID_OPTIONS = {
    "Nervous": {
        "viz": {"Surface": True, "Clipping": True, "Curved MPR": False},
        "nav": {"Focus": True, "Moving-Illustration": False, "Fly-through": False}
    },
    "Cardiovascular": {
        "viz": {"Surface": True, "Clipping": True, "Curved MPR": True},
        "nav": {"Focus": True, "Moving-Illustration": True, "Fly-through": True}
    },
    "Musculoskeletal": {
        "viz": {"Surface": True, "Clipping": True, "Curved MPR": False},
        "nav": {"Focus": True, "Moving-Illustration": False, "Fly-through": False}
    },
    "Mouth/Dental": {
        "viz": {"Surface": True, "Clipping": True, "Curved MPR": True},
        "nav": {"Focus": True, "Moving-Illustration": False, "Fly-through": False}
    }
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Medical Visualization")
        self.resize(1200, 800)

        # Layouts
        container = QWidget()
        layout = QHBoxLayout(container)

        # Left side controls
        left = QVBoxLayout()
        self.system_combo = QComboBox()
        self.system_combo.addItems(SYSTEMS)
        self.system_combo.currentTextChanged.connect(self.update_options)
        left.addWidget(QLabel("Select Anatomical System"))
        left.addWidget(self.system_combo)

        # Visualization
        self.viz_group = QGroupBox("Visualization Method")
        vbox = QVBoxLayout()
        self.viz_radios = {name: QRadioButton(name) for name in ["Surface", "Clipping", "Curved MPR"]}
        for rb in self.viz_radios.values(): vbox.addWidget(rb)
        self.viz_group.setLayout(vbox)
        left.addWidget(self.viz_group)

        # Navigation
        self.nav_group = QGroupBox("Navigation Method")
        nbox = QVBoxLayout()
        self.nav_radios = {name: QRadioButton(name) for name in ["Focus", "Moving-Illustration", "Fly-through"]}
        for rb in self.nav_radios.values(): nbox.addWidget(rb)
        self.nav_group.setLayout(nbox)
        left.addWidget(self.nav_group)

        # Import buttons
        btn_nifti = QPushButton("Import NIfTI")
        btn_nifti.clicked.connect(self.import_nifti)
        btn_csv = QPushButton("Import CSV")
        btn_csv.clicked.connect(self.import_csv)
        left.addWidget(btn_nifti)
        left.addWidget(btn_csv)

        # Render button
        btn_render = QPushButton("Render")
        btn_render.clicked.connect(self.render)
        left.addWidget(btn_render)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        left.addWidget(self.log)

        # Right 3D viewer
        self.plotter = QtInteractor(self)
        layout.addLayout(left, 2)
        layout.addWidget(self.plotter.interactor, 8)
        self.setCentralWidget(container)

        # Variables
        self.nifti_data = None
        self.csv_data = None

        self.update_options(self.system_combo.currentText())

    def update_options(self, system):
        for name, rb in self.viz_radios.items():
            rb.setEnabled(VALID_OPTIONS[system]["viz"][name])
        for name, rb in self.nav_radios.items():
            rb.setEnabled(VALID_OPTIONS[system]["nav"][name])
        self.log.append(f"System changed: {system}")

    def import_nifti(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NIfTI", "", "NIfTI Files (*.nii *.nii.gz)")
        if path:
            self.nifti_data = load_nifti(path)
            self.log.append(f"NIfTI loaded: {path}")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            self.csv_data = load_csv(path)
            self.log.append(f"CSV loaded: {path}")

    def render(self):
        if not self.nifti_data:
            self.log.append("Please import a NIfTI file first.")
            return
        viz = next((n for n, rb in self.viz_radios.items() if rb.isChecked()), "Surface")
        self.plotter.clear()
        surface_render(self.plotter, self.nifti_data)
        self.log.append(f"Rendered using {viz}")


def run_app():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
