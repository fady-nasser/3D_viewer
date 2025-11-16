import nibabel as nib
import numpy as np
from PIL import Image
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import shutil  # 🧹 for deleting old folders

def normalize_intensity(data):
    """Normalize intensity values to 0-255 range"""
    data_min = np.min(data)
    data_max = np.max(data)
    if data_max - data_min == 0:
        return np.zeros_like(data, dtype=np.uint8)
    return ((data - data_min) / (data_max - data_min) * 255).astype(np.uint8)

def generate_slices(nifti_path, output_folder, progress_callback=None):
    """Generate axial, sagittal, and coronal slices from a NIfTI file"""
    try:
        nifti_img = nib.load(nifti_path)
        data = nifti_img.get_fdata()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load NIfTI file:\n{e}")
        return False

    dim_x, dim_y, dim_z = data.shape[:3]
    data_normalized = normalize_intensity(data)

    # Prepare output folders
    axial_folder = os.path.join(output_folder, "Axial")
    sagittal_folder = os.path.join(output_folder, "Sagittal")
    coronal_folder = os.path.join(output_folder, "Coronal")

    # 🧹 Delete existing folders before recreating them
    for folder in [axial_folder, sagittal_folder, coronal_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    os.makedirs(axial_folder, exist_ok=True)
    os.makedirs(sagittal_folder, exist_ok=True)
    os.makedirs(coronal_folder, exist_ok=True)

    total_slices = dim_x + dim_y + dim_z
    count = 0

    # Axial slices
    for z in range(dim_z):
        img = Image.fromarray(np.transpose(data_normalized[:, :, z]), mode='L')
        img.save(os.path.join(axial_folder, f"axial_{z:04d}.png"))
        count += 1
        if progress_callback:
            progress_callback(count / total_slices * 100)

    # Sagittal slices
    for x in range(dim_x):
        img = Image.fromarray(np.transpose(data_normalized[x, :, :]), mode='L')
        img.save(os.path.join(sagittal_folder, f"sagittal_{x:04d}.png"))
        count += 1
        if progress_callback:
            progress_callback(count / total_slices * 100)

    # Coronal slices
    for y in range(dim_y):
        img = Image.fromarray(np.transpose(data_normalized[:, y, :]), mode='L')
        img.save(os.path.join(coronal_folder, f"coronal_{y:04d}.png"))
        count += 1
        if progress_callback:
            progress_callback(count / total_slices * 100)

    # Save dimensions info
    info_file = os.path.join(output_folder, "dimensions.txt")
    with open(info_file, 'w') as f:
        f.write(f"{dim_x},{dim_y},{dim_z}")

    return True

def start_processing(nifti_path, output_folder, root, progress_bar, label):
    def update_progress(value):
        progress_bar["value"] = value
        label.config(text=f"Processing... {int(value)}%")
        root.update_idletasks()

    def process():
        success = generate_slices(nifti_path, output_folder, progress_callback=update_progress)
        if success:
            label.config(text="✅ Done! All slices generated.")
            progress_bar["value"] = 100
            messagebox.showinfo("Success", f"Slices saved to:\n{output_folder}")
        else:
            label.config(text="❌ Failed.")
        root.after(2000, root.destroy)  # Close window after 2 seconds
        root.after(2500, sys.exit)       # Then exit CMD

    threading.Thread(target=process).start()

if __name__ == "__main__":
    output_folder = r"D:\MedicalData\Import"
    os.makedirs(output_folder, exist_ok=True)

    # File dialog
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Select File", "Please select a NIfTI (.nii or .nii.gz) file.")
    nifti_path = filedialog.askopenfilename(
        title="Select NIfTI File",
        filetypes=[("NIfTI files", "*.nii *.nii.gz"), ("All files", "*.*")]
    )
    if not nifti_path:
        messagebox.showwarning("No File Selected", "No file selected. Exiting.")
        sys.exit(0)

    # Progress window
    progress_window = tk.Tk()
    progress_window.title("Generating Slices")
    progress_window.geometry("400x120")
    progress_window.resizable(False, False)

    label = tk.Label(progress_window, text="Preparing...", font=("Segoe UI", 11))
    label.pack(pady=15)

    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    progress_bar["value"] = 0

    start_processing(nifti_path, output_folder, progress_window, progress_bar, label)

    progress_window.mainloop()
