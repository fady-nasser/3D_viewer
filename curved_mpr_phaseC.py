# curved_mpr_phaseC_fixed.py
# Phase C - Curved MPR (CustomTkinter, dark UI, axial slider, no flip normals)

import numpy as np
import nibabel as nib
from scipy.interpolate import splev, splprep, interp1d
from scipy.ndimage import map_coordinates
import imageio
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# --- UI imports ---
try:
    import customtkinter as ctk
    CTK = True
except Exception:
    import tkinter as tk
    from tkinter import filedialog
    CTK = False

# --- Dark theme ---
dark_bg = "#1b1b1b"
dark_axis = "#222222"
plt.rcParams.update({
    "figure.facecolor": dark_bg,
    "axes.facecolor": dark_axis,
    "savefig.facecolor": dark_bg,
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "axes.edgecolor": "white",
})

if CTK:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


# --- arc-length resample ---
def arc_length_resample(x, y, n_samples):
    pts = np.stack([x, y], axis=1)
    seg = np.diff(pts, axis=0)
    dist = np.sqrt((seg**2).sum(axis=1))
    cum = np.concatenate([[0.0], np.cumsum(dist)])
    total = cum[-1]
    if total <= 0 or np.allclose(total, 0.0):
        return np.full(n_samples, x[0]), np.full(n_samples, y[0])
    target_s = np.linspace(0, total, n_samples)
    fx = interp1d(cum, x, kind="linear", bounds_error=False, fill_value=(x[0], x[-1]))
    fy = interp1d(cum, y, kind="linear", bounds_error=False, fill_value=(y[0], y[-1]))
    xs = fx(target_s)
    ys = fy(target_s)
    return xs, ys


# --- main app ---
class CurvedMPRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Curved MPR — Phase C (Improved)")
        self.root.geometry("1250x850")

        self.data_3d = None
        self.axial_slice = None
        self.slice_index = 0
        self.path_display = []
        self.path_data = []
        self.num_samples = 1000
        self.thickness_px = 60
        self.z_half = 10
        self.interpolate_order = 3
        self.rot_k = 0
        self.last_panorama = None

        self.build_ui()

    def build_ui(self):
        if CTK:
            Frame = ctk.CTkFrame
            Button = ctk.CTkButton
            Label = ctk.CTkLabel
            Slider = ctk.CTkSlider
        else:
            import tkinter as tk
            from tkinter import Scale as Slider
            Frame = tk.Frame
            Button = tk.Button
            Label = tk.Label

        # --- First row of controls ---
        top = Frame(self.root)
        top.pack(side="top", fill="x", padx=6, pady=6)

        self.btn_load = Button(top, text="Load NIfTI", command=self.load_nifti, width=14)
        self.btn_load.pack(side="left", padx=4)

        self.slice_label = Label(top, text="Axial slice: 0")
        self.slice_label.pack(side="left", padx=(8, 2))

        self.slice_slider = Slider(top, from_=0, to=1, command=self.on_slice_change, width=360)
        self.slice_slider.set(0)
        try:
            self.slice_slider.configure(state="disabled")
        except Exception:
            pass
        self.slice_slider.pack(side="left", padx=2)

        self.btn_clear = Button(top, text="Clear Path", command=self.clear_path, state="disabled", width=12)
        self.btn_clear.pack(side="left", padx=4)

        self.btn_generate = Button(top, text="Generate Panorama (3D)", command=self.generate_panorama, state="disabled", width=20)
        self.btn_generate.pack(side="left", padx=6)

        self.btn_export = Button(top, text="Export PNG", command=self.export_png, state="disabled", width=12)
        self.btn_export.pack(side="left", padx=6)

        self.btn_rotate = Button(top, text="Rotate Axial 90°", command=self.rotate_axial, width=16)
        self.btn_rotate.pack(side="left", padx=6)

        # --- Second row of controls ---
        bottom_controls = Frame(self.root)
        bottom_controls.pack(side="top", fill="x", padx=6, pady=(0, 6))

        lbl_samples = Label(bottom_controls, text=f"Samples: {self.num_samples}")
        lbl_samples.pack(side="left", padx=(4, 2))
        self.lbl_samples = lbl_samples
        self.samp_slider = Slider(bottom_controls, from_=200, to=2000, command=self.on_samples_change, width=200)
        self.samp_slider.set(self.num_samples)
        self.samp_slider.pack(side="left", padx=2)

        lbl_thick = Label(bottom_controls, text=f"Thickness px: {self.thickness_px}")
        lbl_thick.pack(side="left", padx=(10, 2))
        self.lbl_thick = lbl_thick
        self.thick_slider = Slider(bottom_controls, from_=8, to=200, command=self.on_thickness_change, width=200)
        self.thick_slider.set(self.thickness_px)
        self.thick_slider.pack(side="left", padx=2)

        lbl_z = Label(bottom_controls, text=f"Z half-extent: {self.z_half}")
        lbl_z.pack(side="left", padx=(10, 2))
        self.lbl_z = lbl_z
        self.z_slider = Slider(bottom_controls, from_=0, to=60, command=self.on_z_change, width=200)
        self.z_slider.set(self.z_half)
        self.z_slider.pack(side="left", padx=2)

        # --- Canvas frame ---
        canvas_frame = Frame(self.root)
        canvas_frame.pack(side="top", fill="both", expand=True, padx=6, pady=6)

        self.fig = plt.Figure(figsize=(7, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Axial Slice - Load a NIfTI")
        self.ax.set_facecolor(dark_axis)

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, canvas_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.on_click)

    # --- slider callbacks ---
    def on_samples_change(self, v):
        self.num_samples = int(float(v))
        self.lbl_samples.configure(text=f"Samples: {self.num_samples}")

    def on_thickness_change(self, v):
        self.thickness_px = int(float(v))
        self.lbl_thick.configure(text=f"Thickness px: {self.thickness_px}")

    def on_z_change(self, v):
        self.z_half = int(float(v))
        self.lbl_z.configure(text=f"Z half-extent: {self.z_half}")

    def on_slice_change(self, v):
        if self.data_3d is None:
            return
        idx = int(float(v))
        idx = np.clip(idx, 0, self.data_3d.shape[2]-1)
        self.slice_index = idx
        self.slice_label.configure(text=f"Axial slice: {self.slice_index}")
        self.update_axial()

    # --- load nifti ---
    def load_nifti(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("NIfTI", "*.nii *.nii.gz")])
        if not path:
            return
        img = nib.load(path)
        data = img.get_fdata().astype(np.float32)
        if data.ndim == 4:
            data = data[..., 0]
        self.data_3d = data
        self.slice_index = int(self.data_3d.shape[2] // 2)
        maxz = max(1, self.data_3d.shape[2]-1)
        self.slice_slider.configure(to=maxz, state="normal")
        self.slice_slider.set(self.slice_index)
        self.update_axial()
        print("Loaded:", data.shape)

    # --- axial display ---
    def update_axial(self):
        z = self.slice_index
        z0 = max(0, z-1)
        z1 = min(self.data_3d.shape[2], z+1)
        slab = self.data_3d[:, :, z0:z1]
        self.axial_slice = np.max(slab, axis=2)
        self.draw_axial()

    def draw_axial(self):
        arr = np.rot90(self.axial_slice, k=self.rot_k)
        self.display_image = arr
        self.ax.clear()
        self.ax.imshow(arr, cmap="gray", origin="upper")
        xs = [p[0] for p in self.path_display]
        ys = [p[1] for p in self.path_display]
        self.ax.plot(xs, ys, 'r-o', markersize=4)
        self.ax.set_title(f"Axial slice {self.slice_index}", color="white")
        self.ax.set_facecolor(dark_axis)
        self.canvas.draw_idle()

    def rotate_axial(self):
        self.rot_k = (self.rot_k + 1) % 4
        new_disp = [self.data_to_display_coords(r, c) for (r, c) in self.path_data]
        self.path_display = new_disp
        self.draw_axial()

    # --- click to add ---
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        x_d, y_d = event.xdata, event.ydata
        self.path_display.append((x_d, y_d))
        r, c = self.display_to_data_coords(x_d, y_d)
        self.path_data.append((r, c))
        if len(self.path_data) >= 4:
            self.btn_generate.configure(state="normal")
        self.btn_clear.configure(state="normal")
        self.draw_axial()

    # --- coords ---
    def display_to_data_coords(self, x_d, y_d):
        H, W = self.axial_slice.shape
        if self.rot_k == 0:
            return y_d, x_d
        elif self.rot_k == 1:
            return x_d, (H - 1) - y_d
        elif self.rot_k == 2:
            return (H - 1) - y_d, (W - 1) - x_d
        elif self.rot_k == 3:
            return (W - 1) - x_d, y_d
        return y_d, x_d

    def data_to_display_coords(self, r, c):
        H, W = self.axial_slice.shape
        if self.rot_k == 0:
            return c, r
        elif self.rot_k == 1:
            return r, (H - 1) - c
        elif self.rot_k == 2:
            return (W - 1) - c, (H - 1) - r
        elif self.rot_k == 3:
            return (H - 1) - r, c
        return c, r

    def clear_path(self):
        self.path_display = []
        self.path_data = []
        self.btn_clear.configure(state="disabled")
        self.btn_generate.configure(state="disabled")
        self.draw_axial()

    # --- generate panorama (نفس الخوارزمية الأصلية) ---
    def generate_panorama(self):
        if self.data_3d is None or len(self.path_data) < 4:
            return
        path = np.array(self.path_data)
        rows, cols = path[:,0], path[:,1]
        k = min(3, max(1, len(rows)-1))
        tck, u = splprep([rows, cols], s=3.0, k=k)
        u_fine = np.linspace(0.0, 1.0, max(len(rows)*10, 200))
        r_fine, c_fine = splev(u_fine, tck)
        r_samp, c_samp = arc_length_resample(r_fine, c_fine, int(self.num_samples))
        dr, dc = np.gradient(r_samp), np.gradient(c_samp)
        mag = np.sqrt(dr**2 + dc**2)+1e-12
        tr, tc = dr/mag, dc/mag
        nr, nc = -tc, tr
        tpos = np.linspace(-(self.thickness_px-1)/2, (self.thickness_px-1)/2, self.thickness_px)
        z0 = max(0, self.slice_index - self.z_half)
        z1 = min(self.data_3d.shape[2], self.slice_index + self.z_half + 1)
        z_levels = np.arange(z0, z1)
        grid_shape = (len(tpos), len(r_samp), len(z_levels))
        rows_base = np.broadcast_to(r_samp[None,:,None], grid_shape)
        cols_base = np.broadcast_to(c_samp[None,:,None], grid_shape)
        nr_grid = np.broadcast_to(nr[None,:,None], grid_shape)
        nc_grid = np.broadcast_to(nc[None,:,None], grid_shape)
        t_grid = np.broadcast_to(tpos[:,None,None], grid_shape)
        z_grid = np.broadcast_to(z_levels[None,None,:], grid_shape)
        samp_r = rows_base + nr_grid*t_grid
        samp_c = cols_base + nc_grid*t_grid
        samp_z = z_grid
        coords = np.vstack([samp_r.ravel(), samp_c.ravel(), samp_z.ravel()])
        sampled = map_coordinates(self.data_3d, coords, order=3, mode='nearest')
        pano = np.max(sampled.reshape(grid_shape), axis=2)
        self.last_panorama = pano
        self.btn_export.configure(state="normal")
        self.show_panorama_window(pano)

    def export_png(self):
        if self.last_panorama is None:
            return
        from tkinter import filedialog
        p = filedialog.asksaveasfilename(defaultextension=".png")
        if not p:
            return
        img = self.last_panorama
        mn, mx = np.min(img), np.max(img)
        if mx - mn > 0:
            img = (img - mn)/(mx - mn)
        imageio.imwrite(p, (img*255).astype(np.uint8))
        print("Saved to", p)

    def show_panorama_window(self, pano):
        top = ctk.CTkToplevel() if CTK else tk.Toplevel()
        top.title("Curved MPR Panorama")
        fig = plt.Figure(figsize=(10,5), dpi=100)
        ax = fig.add_subplot(111)
        ax.imshow(pano, cmap="gray", aspect="auto", origin="lower")
        ax.set_title("Curved MPR (MIP along Z)")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        NavigationToolbar2Tk(canvas, top).update()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)


if __name__ == "__main__":
    root = ctk.CTk() if CTK else tk.Tk()
    app = CurvedMPRApp(root)
    root.mainloop()