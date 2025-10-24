# ui/main_window.py
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QGroupBox, QStackedWidget,
    QSizePolicy, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
import sys
import importlib
import os

# ---------------- CONFIGURATION ----------------

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


class WizardUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Medical Visualization Wizard")
        self.resize(900, 620)

        self._style()
        self.stack = QStackedWidget()

        self.page_system = self._page_system()
        self.page_visualization = self._page_visualization()
        self.page_navigation = self._page_navigation()
        self.page_summary = self._page_summary()

        for p in [self.page_system, self.page_visualization, self.page_navigation, self.page_summary]:
            self.stack.addWidget(p)

        # main layout
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

        # vars
        self.page_history = []
        self.selected_system = None
        self.selected_visualization = None
        self.selected_navigation = None
        self.nifti_path = None
        self.csv_path = None

    # ---------------- UI BUILD ----------------

    def _style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QLabel#title { font-size: 24px; font-weight: bold; color: #111; margin-bottom: 25px; }
            QPushButton {
                background-color: #e0e7ff; border: none; border-radius: 12px;
                padding: 14px 22px; font-size: 15px; color: #1e3a8a; font-weight: 500;
            }
            QPushButton:hover { background-color: #c7d2fe; }
            QPushButton[selected="true"] { background-color: #1e40af; color: white; font-weight: bold; }
            QPushButton#back { background-color: transparent; color: #1e3a8a; font-weight: bold; }
            QGroupBox { border: 2px solid #e5e7eb; border-radius: 10px; padding: 10px;
                        font-weight: bold; color: #111827; background-color: #fbfcfe; }
            QRadioButton { font-size: 15px; color: #111827; padding: 3px; }
            QRadioButton:disabled { color: #9ca3af; }
            QLabel#status_bad { color: #991b1b; font-weight: bold; }
            QLabel#status_ok { color: #065f46; font-weight: bold; }
        """)

    def _page_system(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Step 1: Choose Anatomical System")
        label.setObjectName("title")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        hbox = QHBoxLayout()
        hbox.setSpacing(20)
        hbox.setAlignment(Qt.AlignCenter)
        self.system_buttons = {}
        for name in SYSTEMS:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, n=name: self.select_system(n))
            self.system_buttons[name] = btn
            hbox.addWidget(btn)
        layout.addLayout(hbox)
        return page

    def _page_visualization(self):
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
        layout.addWidget(self.viz_group)
        return page

    def _page_navigation(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Step 3: Choose Navigation Method")
        label.setObjectName("title")
        layout.addWidget(label)
        self.nav_group = QGroupBox("Navigation Methods")
        vbox = QVBoxLayout()
        self.nav_radios = {}
        for name in ["Focus Navigation", "Moving Illustration", "Fly-through"]:
            rb = QRadioButton(name)
            rb.toggled.connect(lambda checked, n=name, r=rb: self.navigation_selected(checked, n, r))
            self.nav_radios[name] = rb
            vbox.addWidget(rb)
        self.nav_group.setLayout(vbox)
        layout.addWidget(self.nav_group)
        return page

    def _page_summary(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel("Step 4: Import Files (NIfTI + CSV)")
        label.setObjectName("title")
        layout.addWidget(label)

        # import buttons
        files_box = QHBoxLayout()
        files_box.setSpacing(30)
        files_box.setAlignment(Qt.AlignCenter)

        self.btn_nifti = QPushButton("Import NIfTI (.nii / .nii.gz)")
        self.btn_nifti.clicked.connect(self.import_nifti)
        self.lbl_nifti = QLabel("No file loaded"); self.lbl_nifti.setObjectName("status_bad")

        self.btn_csv = QPushButton("Import CSV")
        self.btn_csv.clicked.connect(self.import_csv)
        self.lbl_csv = QLabel("No file loaded"); self.lbl_csv.setObjectName("status_bad")

        col1, col2 = QVBoxLayout(), QVBoxLayout()
        col1.addWidget(self.btn_nifti); col1.addWidget(self.lbl_nifti)
        col2.addWidget(self.btn_csv); col2.addWidget(self.lbl_csv)
        files_box.addLayout(col1); files_box.addLayout(col2)
        layout.addLayout(files_box)

        self.finish_btn = QPushButton("Finish and Visualize")
        self.finish_btn.clicked.connect(self.finish_and_run)
        self.finish_btn.setEnabled(False)
        layout.addWidget(self.finish_btn, alignment=Qt.AlignCenter)
        return page

    # ---------------- LOGIC ----------------

    def select_system(self, system):
        self.selected_system = system
        for name, btn in self.system_buttons.items():
            btn.setProperty("selected", str(name == system).lower())
            btn.style().unpolish(btn); btn.style().polish(btn)
        for name, rb in self.viz_radios.items():
            rb.setEnabled(VALID_OPTIONS[system]["viz"][name])
            rb.setChecked(False)
        self.go_to_page(self.page_visualization)

    def visualization_selected(self, checked, viz_name, rb):
        if not checked: return
        self.selected_visualization = viz_name
        system = self.selected_system
        for name, r in self.nav_radios.items():
            r.setEnabled(VALID_OPTIONS[system]["nav"][name])
            r.setChecked(False)
        self.go_to_page(self.page_navigation)

    def navigation_selected(self, checked, nav_name, rb):
        if not checked:
            return
        self.selected_navigation = nav_name
        self.go_to_page(self.page_summary)

        # ✅ Reset paths
        self.nifti_path = None
        self.csv_path = None
        self.lbl_nifti.setText("No file loaded")
        self.lbl_csv.setText("No file loaded")
        self.finish_btn.setEnabled(False)

        # ✅ Show/Hide CSV import based on navigation method
        if nav_name == "Moving Illustration":
            self.btn_csv.show()
            self.lbl_csv.show()
        else:
            self.btn_csv.hide()
            self.lbl_csv.hide()

    def import_nifti(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NIfTI file", "", "NIfTI Files (*.nii *.nii.gz)")
        if path:
            if not path.lower().endswith((".nii", ".nii.gz")):
                QMessageBox.warning(self, "Invalid File", "Please select a valid NIfTI (.nii / .nii.gz) file.")
                return
            self.nifti_path = path
            self.lbl_nifti.setText(os.path.basename(path))
            self.lbl_nifti.setObjectName("status_ok")
            self.lbl_nifti.style().unpolish(self.lbl_nifti)
            self.lbl_nifti.style().polish(self.lbl_nifti)
            self._update_finish_btn()

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV file", "", "CSV Files (*.csv)")
        if path:
            if not path.lower().endswith(".csv"):
                QMessageBox.warning(self, "Invalid File", "Please select a valid CSV file.")
                return
            self.csv_path = path
            self.lbl_csv.setText(os.path.basename(path))
            self.lbl_csv.setObjectName("status_ok")
            self.lbl_csv.style().unpolish(self.lbl_csv)
            self.lbl_csv.style().polish(self.lbl_csv)
            self._update_finish_btn()

    def _update_finish_btn(self):
        csv_required = (self.selected_navigation == "Moving Illustration")

        if self.nifti_path and (self.csv_path or not csv_required):
            self.finish_btn.setEnabled(True)
        else:
            self.finish_btn.setEnabled(False)

    # --------- 🧠 FINAL STEP: Run selected modules ---------
    def finish_and_run(self):
        csv_required = (self.selected_navigation == "Moving Illustration")

        if not self.nifti_path:
            QMessageBox.warning(self, "Missing File", "Please select a NIfTI file first.")
            return

        if csv_required and not self.csv_path:
            QMessageBox.warning(self, "Missing CSV", "This navigation method requires a CSV file.")
            return

        viz_func = self._import_visualization()
        nav_func = self._import_navigation()

        if viz_func and nav_func:
            viz_func(self.nifti_path)
            if csv_required:
                nav_func(self.csv_path)
            else:
                nav_func()
        else:
            QMessageBox.warning(self, "Error", "Failed to load selected visualization/navigation module.")


    def _import_visualization(self):
        name = self.selected_visualization.lower().replace(" ", "_")
        try:
            module = importlib.import_module(f"visualization.{name}")
            return getattr(module, f"visualize_{name}")
        except Exception as e:
            print("Visualization import error:", e)
            return None

    def _import_navigation(self):
        name = self.selected_navigation.lower().replace(" ", "_").replace("-", "_")
        try:
            module = importlib.import_module(f"navigation.{name}")
            return getattr(module, f"start_{name}")
        except Exception as e:
            print("Navigation import error:", e)
            return None

    # ---------------- BACK ----------------
    def go_to_page(self, page):
        current_index = self.stack.currentIndex()
        self.page_history.append(current_index)
        self.stack.setCurrentWidget(page)
        self.back_button.show()

     # ---------------- BACK ----------------
    def go_back(self):
        """Handle Back button and clear previous selections."""
        if not self.page_history:
            return

        current_page = self.stack.currentWidget()
        prev_index = self.page_history.pop()

        # 🧹 clear selections depending on which page you're going back from
        if current_page == self.page_visualization:
            # رجع من Visualization → System ⇒ امسح الـ System selection
            self.selected_system = None
            for btn in self.system_buttons.values():
                btn.setProperty("selected", "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

        elif current_page == self.page_navigation:
            # رجع من Navigation → Visualization ⇒ امسح الـ Visualization selection
            self.selected_visualization = None
            for rb in self.viz_radios.values():
                rb.setAutoExclusive(False)
                rb.setChecked(False)
                rb.setAutoExclusive(True)

        elif current_page == self.page_summary:
            # رجع من Summary → Navigation ⇒ امسح الـ Navigation selection
            self.selected_navigation = None
            for rb in self.nav_radios.values():
                rb.setAutoExclusive(False)
                rb.setChecked(False)
                rb.setAutoExclusive(True)
            # كمان امسح الملفات اللي كان محمّلها
            self.nifti_path = None
            self.csv_path = None
            self.lbl_nifti.setText("No file loaded")
            self.lbl_csv.setText("No file loaded")
            self.finish_btn.setEnabled(False)

        # 👇 روح فعليًا للصفحة اللي قبلها
        self.stack.setCurrentIndex(prev_index)

        # اخفي الزرار لو رجع لأول صفحة
        if not self.page_history:
            self.back_button.hide()



def run_app():
    app = QApplication(sys.argv)
    win = WizardUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
