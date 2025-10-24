# main.py
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QGroupBox, QStackedWidget,
    QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt
import sys
import os

# ---------- CONFIGURATION ----------
SYSTEMS = ["Nervous System", "Cardiovascular System", "Musculoskeletal System", "Mouth/Dental System"]

VALID_OPTIONS = {
    "Nervous System": {
        "viz": {"Surface Rendering": True, "Clipping Planes": True, "Curved MPR": False},
        "nav": {"Focus Navigation": True, "Moving Illustration": False, "Fly-through": False}
    },
    "Cardiovascular System": {
        "viz": {"Surface Rendering": True, "Clipping Planes": True, "Curved MPR": True},
        "nav": {"Focus Navigation": True, "Moving Illustration": True, "Fly-through": True}
    },
    "Musculoskeletal System": {
        "viz": {"Surface Rendering": True, "Clipping Planes": True, "Curved MPR": False},
        "nav": {"Focus Navigation": True, "Moving Illustration": False, "Fly-through": False}
    },
    "Mouth/Dental System": {
        "viz": {"Surface Rendering": True, "Clipping Planes": True, "Curved MPR": True},
        "nav": {"Focus Navigation": True, "Moving Illustration": False, "Fly-through": False}
    },
}

try:
    import nibabel as nib
    HAVE_NIBABEL = True
except Exception:
    HAVE_NIBABEL = False

try:
    import pandas as pd
    HAVE_PANDAS = True
except Exception:
    HAVE_PANDAS = False


class WizardUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Medical Visualization Wizard")
        self.resize(900, 620)

        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QLabel#title { font-size: 24px; font-weight: bold; color: #222; margin-bottom: 18px; }
            QPushButton { background-color: #e0e7ff; border: none; border-radius: 10px;
                          padding: 12px 18px; font-size: 15px; color: #1e3a8a; font-weight: 500; }
            QPushButton:hover { background-color: #c7d2fe; }
            QPushButton[selected="true"] { background-color: #1e40af; color: white; font-weight: bold; }
            QPushButton#back { background-color: transparent; color: #1e3a8a; font-weight: bold; }
            QGroupBox { border: 2px solid #e5e7eb; border-radius: 10px; padding: 10px; font-weight: bold;
                        color: #111827; background-color: #fbfcfe; }
            QRadioButton { font-size: 15px; color: #111827; padding: 3px; }
            QRadioButton:disabled { color: #9ca3af; }
            QLabel#small { font-size: 13px; color: #374151; }
            QLabel#status_ok { color: #065f46; font-weight: bold; }
            QLabel#status_bad { color: #991b1b; font-weight: bold; }
        """)

        self.stack = QStackedWidget()
        self.page_system = self.create_system_page()
        self.page_visualization = self.create_visualization_page()
        self.page_navigation = self.create_navigation_page()
        self.page_summary = self.create_summary_page()

        self.stack.addWidget(self.page_system)
        self.stack.addWidget(self.page_visualization)
        self.stack.addWidget(self.page_navigation)
        self.stack.addWidget(self.page_summary)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(18, 18, 18, 18)

        top_bar = QHBoxLayout()
        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("back")
        self.back_button.setFixedWidth(90)
        self.back_button.clicked.connect(self.go_back)
        top_bar.addWidget(self.back_button, alignment=Qt.AlignLeft)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.stack)
        self.setCentralWidget(main_widget)
        self.back_button.hide()

        self.selected_system = None
        self.selected_visualization = None
        self.selected_navigation = None
        self.page_history = []

        self.nifti_path = None
        self.csv_path = None

    def create_system_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Step 1: Choose Anatomical System")
        label.setObjectName("title")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setSpacing(18)
        center_layout.setAlignment(Qt.AlignCenter)
        center_container.setMaximumWidth(760)

        self.system_buttons = {}
        for name in SYSTEMS:
            btn = QPushButton(name)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(lambda checked, n=name: self.select_system(n))
            self.system_buttons[name] = btn
            center_layout.addWidget(btn)

        layout.addWidget(center_container)
        hint = QLabel("Choose the anatomical system you want to visualize")
        hint.setObjectName("small")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        return page

    def create_visualization_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Step 2: Choose Visualization Method")
        label.setObjectName("title")
        layout.addWidget(label)

        self.viz_group = QGroupBox("Visualization Methods")
        vbox = QVBoxLayout()
        self.viz_radios = {}
        for name in ["Surface Rendering", "Clipping Planes", "Curved MPR"]:
            rb = QRadioButton(name)
            rb.toggled.connect(lambda checked, n=name, r=rb: self.visualization_selected(checked, n, r))
            self.viz_radios[name] = rb
            vbox.addWidget(rb)
        self.viz_group.setLayout(vbox)
        self.viz_group.setFixedWidth(520)
        layout.addWidget(self.viz_group)
        return page

    def create_navigation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Step 3: Choose Navigation Method")
        label.setObjectName("title")
        layout.addWidget(label)

        self.nav_group = QGroupBox("Navigation Methods")
        nbox = QVBoxLayout()
        self.nav_radios = {}
        for name in ["Focus Navigation", "Moving Illustration", "Fly-through"]:
            rb = QRadioButton(name)
            rb.toggled.connect(lambda checked, n=name, r=rb: self.navigation_selected(checked, n, r))
            self.nav_radios[name] = rb
            nbox.addWidget(rb)
        self.nav_group.setLayout(nbox)
        self.nav_group.setFixedWidth(520)
        layout.addWidget(self.nav_group)
        return page

    def create_summary_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Step 4: Import Files (NIfTI + CSV)")
        label.setObjectName("title")
        layout.addWidget(label)

        files_widget = QWidget()
        files_layout = QHBoxLayout(files_widget)
        files_layout.setSpacing(30)
        files_layout.setAlignment(Qt.AlignCenter)
        files_widget.setMaximumWidth(760)

        nifti_col = QVBoxLayout()
        nifti_btn = QPushButton("Import NIfTI (.nii / .nii.gz)")
        nifti_btn.clicked.connect(self.import_nifti)
        self.nifti_status_label = QLabel("No file loaded")
        self.nifti_status_label.setObjectName("status_bad")
        self.nifti_status_label.setAlignment(Qt.AlignCenter)
        nifti_col.addWidget(nifti_btn)
        nifti_col.addWidget(self.nifti_status_label)

        csv_col = QVBoxLayout()
        csv_btn = QPushButton("Import CSV")
        csv_btn.clicked.connect(self.import_csv)
        self.csv_status_label = QLabel("No file loaded")
        self.csv_status_label.setObjectName("status_bad")
        self.csv_status_label.setAlignment(Qt.AlignCenter)
        csv_col.addWidget(csv_btn)
        csv_col.addWidget(self.csv_status_label)

        files_layout.addLayout(nifti_col)
        files_layout.addLayout(csv_col)
        layout.addWidget(files_widget)


        self.finish_btn = QPushButton("Finish and Save Selection")
        self.finish_btn.clicked.connect(self.finish_and_save)
        self.finish_btn.setEnabled(False)
        layout.addWidget(self.finish_btn, alignment=Qt.AlignCenter)

        return page

    # --- logic ---
    def select_system(self, system):
        self.selected_system = system
        for name, btn in self.system_buttons.items():
            btn.setProperty("selected", str(name == system).lower())
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        for name, rb in self.viz_radios.items():
            rb.setEnabled(VALID_OPTIONS[system]["viz"][name])
            rb.setChecked(False)
        self.go_to_page(self.page_visualization)

    def visualization_selected(self, checked, viz_name, rb):
        if not checked or rb is None:
            return
        self.selected_visualization = viz_name
        system = self.selected_system
        for name, r in self.nav_radios.items():
            r.setEnabled(VALID_OPTIONS[system]["nav"][name])
            r.setChecked(False)
        self.go_to_page(self.page_navigation)

    def navigation_selected(self, checked, nav_name, rb):
        if not checked or rb is None:
            return
        self.selected_navigation = nav_name
        self.go_to_page(self.page_summary)
        self.nifti_path = None
        self.csv_path = None
        self.nifti_status_label.setText("No file loaded")
        self.csv_status_label.setText("No file loaded")
        self.finish_btn.setEnabled(False)

    def import_nifti(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NIfTI file", "", "NIfTI Files (*.nii *.nii.gz);;All files (*.*)")
        if not path:
            return
        ok, msg = self.validate_nifti(path)
        self.nifti_path = path if ok else None
        self.nifti_status_label.setText(os.path.basename(path) if ok else msg)
        self.nifti_status_label.setObjectName("status_ok" if ok else "status_bad")
        self.nifti_status_label.style().unpolish(self.nifti_status_label)
        self.nifti_status_label.style().polish(self.nifti_status_label)
        self._update_finish_enabled()

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV file", "", "CSV Files (*.csv);;All files (*.*)")
        if not path:
            return
        ok, msg = self.validate_csv(path)
        self.csv_path = path if ok else None
        self.csv_status_label.setText(os.path.basename(path) if ok else msg)
        self.csv_status_label.setObjectName("status_ok" if ok else "status_bad")
        self.csv_status_label.style().unpolish(self.csv_status_label)
        self.csv_status_label.style().polish(self.csv_status_label)
        self._update_finish_enabled()

    def validate_nifti(self, path):
        if path.lower().endswith((".nii", ".nii.gz")):
            if HAVE_NIBABEL:
                try:
                    img = nib.load(path)
                    data = img.get_fdata(dtype='float32')
                    if data.ndim < 3:
                        return False, "File is not 3D"
                    return True, "Valid NIfTI"
                except Exception as e:
                    return False, str(e)
            return True, "Valid by extension"
        return False, "Invalid extension"

    def validate_csv(self, path):
        if path.lower().endswith(".csv"):
            if HAVE_PANDAS:
                try:
                    pd.read_csv(path, nrows=5)
                    return True, "Valid CSV"
                except Exception as e:
                    return False, str(e)
            return True, "Valid by extension"
        return False, "Invalid extension"

    def _update_finish_enabled(self):
        self.finish_btn.setEnabled(bool(self.nifti_path and self.csv_path))

    def finish_and_save(self):
        msg = (
            f"✅ System: {self.selected_system}\n"
            f"🎨 Visualization: {self.selected_visualization}\n"
            f"🧭 Navigation: {self.selected_navigation}\n"
            f"📁 NIfTI: {self.nifti_path}\n"
            f"📊 CSV: {self.csv_path}"
        )
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Selection Complete", msg)

    def go_to_page(self, page):
        current_index = self.stack.currentIndex()
        self.page_history.append(current_index)
        self.stack.setCurrentWidget(page)
        self.back_button.show()

    def go_back(self):
        if not self.page_history:
            return
        prev_index = self.page_history.pop()
        self.stack.setCurrentIndex(prev_index)
        if not self.page_history:
            self.back_button.hide()


def run_app():
    app = QApplication(sys.argv)
    win = WizardUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
