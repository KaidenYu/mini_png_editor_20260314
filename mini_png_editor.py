import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
from PIL import Image, ImageTk, ImageDraw
import threading
import argparse
import json
from typing import Optional, Any

# --- DLL Loading for AI (Windows) ---
# Tell Python to also look for DLLs in our local 'lib' directory
if sys.platform == "win32":
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(current_dir, "lib")
    
    if os.path.exists(lib_path):
        try:
            # os.add_dll_directory is highly recommended for Python 3.8+ on Windows
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(lib_path)
            
            # Add to PATH as well to ensure all loading mechanisms see it
            os.environ["PATH"] = lib_path + os.pathsep + os.environ["PATH"]
            print(f"DEBUG: Added local lib to DLL path: {lib_path}")
        except Exception as e:
            print(f"Warning: Could not add local lib directory: {e}")

# --- Settings & Conditional Imports ---
import settings

HAS_REMBG = False
if getattr(settings, "ENABLE_REMBG", False):
    try:
        from rembg import remove
        HAS_REMBG = True
    except ImportError:
        HAS_REMBG = False

try:
    import windnd
    HAS_WINDND = True
except ImportError:
    HAS_WINDND = False

class PngCropperApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PNG Image Cropper - 1:1 View")
        self.root.geometry("1000x800")
        
        # --- State Variables ---
        self.image_path: Optional[str] = None
        self.original_image: Optional[Image.Image] = None  # Original file
        self.scaled_image: Optional[Image.Image] = None    # Resized data for cropping
        self.tk_image: Optional[ImageTk.PhotoImage] = None  # Processed for display
        
        self.rect_id: Optional[int] = None
        self.rect_x = tk.IntVar(value=20)
        self.rect_y = tk.IntVar(value=20)
        self.rect_width = tk.IntVar(value=100)
        self.rect_height = tk.IntVar(value=100)
        self.cross_h_id: Optional[int] = None
        self.cross_v_id: Optional[int] = None
        
        # --- Display & Scaling ---
        self.scaling_x = 1.0       # Real image width factor
        self.scaling_y = 1.0       # Real image height factor
        self.zoom_level = 1.0      # Visual only zoom
        self.zoom_var = tk.StringVar(value="100")
        self.keep_aspect = tk.BooleanVar(value=True)
        
        self.img_scale_w = tk.IntVar(value=0)
        self.img_scale_h = tk.IntVar(value=0)
        
        self.is_dragging = False
        self.is_resizing = False
        self.is_scaling_img = False
        self.resize_corner: Optional[str] = None
        self.scale_corner: Optional[str] = None
        self.drag_last_x = 0.0
        self.drag_last_y = 0.0
        self.is_full = tk.BooleanVar(value=False)
        self.show_crosshair = tk.BooleanVar(value=False)

        self.setup_ui()
        
        # --- Initialize Drag & Drop ---
        if HAS_WINDND:
            # We wait a bit to ensure the window handle is ready
            self.root.after(500, lambda: windnd.hook_dropfiles(self.root, self.on_file_drop))

    def setup_ui(self):
        # 1. Top Toolbar (Categorized Layout)
        self.toolbar = tk.Frame(self.root, pady=5, padx=10)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # --- Group 1: File ---
        file_group = tk.LabelFrame(self.toolbar, text=" File ", padx=10, pady=5)
        file_group.pack(side=tk.LEFT, padx=5)
        self.btn_open = tk.Button(file_group, text="Open PNG", command=self.open_file_dialog)
        self.btn_open.pack(side=tk.LEFT)
        
        self.btn_save = tk.Button(file_group, text="Save PNG", command=self.crop_and_save, state='disabled')
        self.btn_save.pack(side=tk.LEFT, padx=(10, 0))

        # --- Group 2: Crop Selection ---
        crop_group = tk.LabelFrame(self.toolbar, text=" Crop Selection ", padx=10, pady=5)
        crop_group.pack(side=tk.LEFT, padx=5)
        
        self.check_full = tk.Checkbutton(crop_group, text="Full", variable=self.is_full, command=self.on_full_toggle)
        self.check_full.pack(side=tk.LEFT, padx=(0, 5))

        self.crop_input_container = tk.Frame(crop_group)
        self.crop_input_container.pack(side=tk.LEFT)

        self.check_crosshair = tk.Checkbutton(self.crop_input_container, text="Crosshair", variable=self.show_crosshair, command=self.sync_rect_from_vars)
        self.check_crosshair.pack(side=tk.LEFT, padx=(0, 5))

        for label_text, var in [("X:", self.rect_x), ("Y:", self.rect_y), 
                                ("W:", self.rect_width), ("H:", self.rect_height)]:
            f = tk.Frame(self.crop_input_container)
            f.pack(side=tk.LEFT, padx=2)
            tk.Label(f, text=label_text).pack(side=tk.LEFT)
            tk.Entry(f, textvariable=var, width=4).pack(side=tk.LEFT, padx=2)

        self.btn_reset_crop = tk.Button(self.crop_input_container, text="Reset", command=self.reset_crop, padx=5)
        self.btn_reset_crop.pack(side=tk.LEFT, padx=(5, 5))

        # --- Group 3: Image Scaling ---
        scale_group = tk.LabelFrame(self.toolbar, text=" Image Scaling ", padx=10, pady=5)
        scale_group.pack(side=tk.LEFT, padx=5)
        
        self.check_aspect = tk.Checkbutton(scale_group, text="Lock Aspect", variable=self.keep_aspect)
        self.check_aspect.pack(side=tk.LEFT)
        
        # Manual Dim Inputs (W: H:)
        for label_text, var in [("W:", self.img_scale_w), ("H:", self.img_scale_h)]:
            f = tk.Frame(scale_group)
            f.pack(side=tk.LEFT, padx=2)
            tk.Label(f, text=label_text).pack(side=tk.LEFT)
            tk.Entry(f, textvariable=var, width=5).pack(side=tk.LEFT, padx=2)
            
        self.btn_reset_scale = tk.Button(scale_group, text="Reset", command=self.reset_scaling, padx=5)
        self.btn_reset_scale.pack(side=tk.LEFT, padx=10)
        
        self.img_scale_w.trace_add("write", lambda *a: self.on_img_scale_input("w"))
        self.img_scale_h.trace_add("write", lambda *a: self.on_img_scale_input("h"))

        # --- Group 4: Zoom ---
        zoom_group = tk.LabelFrame(self.toolbar, text=" View (Zoom) ", padx=10, pady=5)
        zoom_group.pack(side=tk.LEFT, padx=5)
        
        tk.Button(zoom_group, text="-", command=self.zoom_out, width=2).pack(side=tk.LEFT)
        self.entry_zoom = tk.Entry(zoom_group, textvariable=self.zoom_var, width=4, justify='center')
        self.entry_zoom.pack(side=tk.LEFT, padx=2)
        tk.Label(zoom_group, text="%").pack(side=tk.LEFT)
        tk.Button(zoom_group, text="+", command=self.zoom_in, width=2).pack(side=tk.LEFT)
        self.zoom_var.trace_add("write", lambda *a: self.on_zoom_input())

        # --- Group 5: AI Tools (Optional) ---
        if HAS_REMBG:
            ai_group = tk.LabelFrame(self.toolbar, text=" AI Tools ", padx=10, pady=5)
            ai_group.pack(side=tk.LEFT, padx=5)
            self.btn_rembg = tk.Button(ai_group, text="Remove BG", command=self.process_remove_bg)
            self.btn_rembg.pack(side=tk.LEFT)
        elif getattr(settings, "ENABLE_REMBG", False):
            # If enabled in settings but missing library
            ai_group = tk.LabelFrame(self.toolbar, text=" AI Tools ", padx=10, pady=5)
            ai_group.pack(side=tk.LEFT, padx=5)
            tk.Label(ai_group, text="rembg not installed", fg="gray").pack()

        # 2. Status Bar (Bottom)
        status_msg = "Ready. Drag a PNG file here to start." if HAS_WINDND else "Ready. Use 'Open PNG' to load image."
        self.status_bar = tk.Label(self.root, text=status_msg, bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 3. Scrolled Canvas Area (View)
        self.canvas_container = tk.Frame(self.root, bg="#424242", bd=1, relief=tk.SUNKEN)
        self.canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.v_scroll = tk.Scrollbar(self.canvas_container, orient=tk.VERTICAL)
        self.h_scroll = tk.Scrollbar(self.canvas_container, orient=tk.HORIZONTAL)
        
        self.canvas = tk.Canvas(
            self.canvas_container, 
            bg="#505050", 
            highlightthickness=0,
            xscrollcommand=self.h_scroll.set, 
            yscrollcommand=self.v_scroll.set
        )
        
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Bindings ---
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_hover)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        
        # Link inputs to rectangle
        self.rect_x.trace_add("write", lambda *a: self.sync_rect_from_vars())
        self.rect_y.trace_add("write", lambda *a: self.sync_rect_from_vars())
        self.rect_width.trace_add("write", lambda *a: self.sync_rect_from_vars())
        self.rect_height.trace_add("write", lambda *a: self.sync_rect_from_vars())

    # --- File Handling ---

    def on_file_drop(self, files: list):
        if not files: return
        
        file_item = files[0]
        path = ""
        
        if isinstance(file_item, bytes):
            # Try to decode with multiple encodings
            for encoding in ['utf-8', 'gbk', 'mbcs', 'ansi']:
                try:
                    path = file_item.decode(encoding)
                    if os.path.exists(path):
                        break
                except UnicodeDecodeError:
                    continue
            else:
                # If all fail, try to use string conversion but it's risky
                path = str(file_item)
        else:
            path = file_item

        # Final check if it's still bytes somehow
        if isinstance(path, bytes):
            path = path.decode('utf-8', errors='ignore')

        # Use root.after to safely execute in main thread
        self.root.after(10, lambda p=path: self.load_image(p))

    def open_file_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All Files", "*.*")])
        if path: self.load_image(path)

    def load_image(self, path: str):
        if not path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            messagebox.showwarning("Warning", "Please select a valid image file.")
            return
            
        try:
            self.image_path = path
            self.original_image = Image.open(path)
            self.tk_image = ImageTk.PhotoImage(self.original_image)
            
            self.scaling_x = 1.0
            self.scaling_y = 1.0
            self.zoom_level = 1.0
            
            self.btn_save.config(state='normal')
            self.refresh_display()
            
            # Initial Rectangle (20,20)
            self.init_crop_rect()
            
            info = f"File: {os.path.basename(path)} | Size: {self.original_image.width} x {self.original_image.height} px"
            self.status_bar.config(text=info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def zoom_in(self):
        if self.zoom_level < 5.0:
            self.zoom_level += 0.1
            self.refresh_display()

    def zoom_out(self):
        if self.zoom_level > 0.1:
            self.zoom_level -= 0.1
            self.refresh_display()

    def refresh_display(self):
        if not self.original_image: return
        
        # 1. Apply real Scaling to the data (Discrete X/Y)
        sw = int(self.original_image.width * self.scaling_x)
        sh = int(self.original_image.height * self.scaling_y)
        # Ensure at least 1px
        sw, sh = max(1, sw), max(1, sh)
        
        self.scaled_image = self.original_image.resize((sw, sh), Image.Resampling.LANCZOS)
        
        # 2. Apply visual Zoom to the view
        vw = int(sw * self.zoom_level)
        vh = int(sh * self.zoom_level)
        view_img = self.scaled_image.resize((vw, vh), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(view_img)
        
        self.canvas.delete("img")
        self.canvas.delete("img_border")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image, tags="img")
        
        # Draw a thin border around the image to show boundaries (especially for transparent images)
        self.canvas.create_rectangle(0, 0, vw, vh, outline="#888888", width=1, tags="img_border")
        
        self.canvas.config(scrollregion=(0, 0, vw, vh))
        
        # Update UI
        self._updating_vars = True
        self.zoom_var.set(str(int(self.zoom_level * 100)))
        self.img_scale_w.set(sw)
        self.img_scale_h.set(sh)
        self._updating_vars = False
        
        self.sync_rect_from_vars()

    def on_zoom_input(self):
        if self._updating_vars or not self.original_image: return
        try:
            val = float(self.zoom_var.get().replace("%", "")) / 100.0
            if 0.01 <= val <= 10.0:
                self.zoom_level = val
                self.refresh_display()
        except: pass

    def on_img_scale_input(self, origin):
        if self._updating_vars or not self.original_image: return
        try:
            target_w = self.img_scale_w.get()
            target_h = self.img_scale_h.get()
            
            if target_w <= 0 or target_h <= 0: return
            
            new_sx = target_w / self.original_image.width
            new_sy = target_h / self.original_image.height
            
            if self.keep_aspect.get():
                if origin == "w":
                    new_sy = new_sx # Mirror factor
                else:
                    new_sx = new_sy
            
            # Apply ratios to rect BEFORE updating scaling factors
            ratio_x = new_sx / self.scaling_x
            ratio_y = new_sy / self.scaling_y
            
            self._updating_vars = True
            self.rect_x.set(int(self.rect_x.get() * ratio_x))
            self.rect_y.set(int(self.rect_y.get() * ratio_y))
            self.rect_width.set(max(1, int(self.rect_width.get() * ratio_x)))
            self.rect_height.set(max(1, int(self.rect_height.get() * ratio_y)))
            
            self.scaling_x = new_sx
            self.scaling_y = new_sy
            self._updating_vars = False
            
            self.refresh_display()
        except: pass

    # --- Rectangle Logic ---

    def init_crop_rect(self):
        self.sync_rect_from_vars()

    def reset_scaling(self):
        if not self.original_image: return
        
        # Calculate ratio to revert back to 1.0
        ratio_x = 1.0 / self.scaling_x
        ratio_y = 1.0 / self.scaling_y
        
        self._updating_vars = True
        # Adjust rect back to original image coordinates
        self.rect_x.set(int(self.rect_x.get() * ratio_x))
        self.rect_y.set(int(self.rect_y.get() * ratio_y))
        self.rect_width.set(max(1, int(self.rect_width.get() * ratio_x)))
        self.rect_height.set(max(1, int(self.rect_height.get() * ratio_y)))
        self._updating_vars = False
        
        self.scaling_x = 1.0
        self.scaling_y = 1.0
        self.refresh_display()

    def reset_crop(self):
        self._updating_vars = True
        self.rect_x.set(0)
        self.rect_y.set(0)
        self.rect_width.set(100)
        self.rect_height.set(100)
        self._updating_vars = False
        self.sync_rect_from_vars()

    def on_full_toggle(self):
        if self.is_full.get():
            self.crop_input_container.pack_forget()
        else:
            self.crop_input_container.pack(side=tk.LEFT)
        self.sync_rect_from_vars()

    def sync_rect_from_vars(self):
        if not self.canvas or not self.original_image: return
        
        # Helper to hide everything if needed
        def hide_all_crop_ui():
            if self.rect_id: self.canvas.itemconfigure(self.rect_id, state='hidden')
            if self.cross_h_id: self.canvas.itemconfigure(self.cross_h_id, state='hidden')
            if self.cross_v_id: self.canvas.itemconfigure(self.cross_v_id, state='hidden')

        if self.is_full.get():
            hide_all_crop_ui()
            return

        try:
            # The vars (x, y, w, h) now represent pixels on the SCALED image.
            # To show them on canvas, we only need to multiply by visual Zoom.
            factor = self.zoom_level
            vx1, vy1 = self.rect_x.get() * factor, self.rect_y.get() * factor
            vx2, vy2 = vx1 + (self.rect_width.get() * factor), vy1 + (self.rect_height.get() * factor)
            
            if self.rect_id:
                self.canvas.coords(self.rect_id, vx1, vy1, vx2, vy2)
                self.canvas.itemconfigure(self.rect_id, state='normal')
                self.canvas.tag_raise(self.rect_id)
            else:
                self.rect_id = self.canvas.create_rectangle(
                    vx1, vy1, vx2, vy2, 
                    outline="red", width=2, dash=(4, 4)
                )

            # --- Crosshair Logic ---
            if self.show_crosshair.get():
                mid_x = (vx1 + vx2) / 2
                mid_y = (vy1 + vy2) / 2
                
                if self.cross_h_id:
                    self.canvas.coords(self.cross_h_id, vx1, mid_y, vx2, mid_y)
                    self.canvas.itemconfigure(self.cross_h_id, state='normal')
                else:
                    self.cross_h_id = self.canvas.create_line(vx1, mid_y, vx2, mid_y, fill="red", dash=(2, 2))
                
                if self.cross_v_id:
                    self.canvas.coords(self.cross_v_id, mid_x, vy1, mid_x, vy2)
                    self.canvas.itemconfigure(self.cross_v_id, state='normal')
                else:
                    self.cross_v_id = self.canvas.create_line(mid_x, vy1, mid_x, vy2, fill="red", dash=(2, 2))
                
                self.canvas.tag_raise(self.cross_h_id)
                self.canvas.tag_raise(self.cross_v_id)
            else:
                if self.cross_h_id: self.canvas.itemconfigure(self.cross_h_id, state='hidden')
                if self.cross_v_id: self.canvas.itemconfigure(self.cross_v_id, state='hidden')

        except: pass

    def update_vars_from_rect(self):
        if not self.rect_id: return
        self._updating_vars = True
        try:
            vx1, vy1, vx2, vy2 = self.canvas.coords(self.rect_id)
            factor = self.zoom_level
            
            # Key fix: Calculate logical boundaries independently 
            # to prevent rounding errors from shifting the 'fixed' edge.
            lx1, ly1 = int(round(vx1 / factor)), int(round(vy1 / factor))
            lx2, ly2 = int(round(vx2 / factor)), int(round(vy2 / factor))
            
            self.rect_x.set(lx1)
            self.rect_y.set(ly1)
            self.rect_width.set(max(1, lx2 - lx1))
            self.rect_height.set(max(1, ly2 - ly1))
        except: pass
        finally:
            self._updating_vars = False

    def get_real_coords(self, event):
        # Base canvas coords (zoomed)
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        # We handle interaction on the zoomed plane
        return cx, cy

    def on_mouse_down(self, event):
        if not self.original_image: return
        rx, ry = self.get_real_coords(event)
        margin = 15
        
        # Scaling detection (Image Corners & Edges)
        vw = self.original_image.width * self.scaling_x * self.zoom_level
        vh = self.original_image.height * self.scaling_y * self.zoom_level
        
        # Bottom-Right Corner Scaling
        if abs(rx - vw) < margin and abs(ry - vh) < margin:
            self.is_scaling_img = True
            self.scale_corner = "se"
            self.drag_last_x, self.drag_last_y = rx, ry
            return
        # Right (East) Edge Scaling
        elif abs(rx - vw) < margin and 0 <= ry <= vh:
            self.is_scaling_img = True
            self.scale_corner = "e"
            self.drag_last_x, self.drag_last_y = rx, ry
            return
        # Bottom (South) Edge Scaling
        elif abs(ry - vh) < margin and 0 <= rx <= vw:
            self.is_scaling_img = True
            self.scale_corner = "s"
            self.drag_last_x, self.drag_last_y = rx, ry
            return

        if not self.is_full.get() and self.rect_id:
            x1, y1, x2, y2 = self.canvas.coords(self.rect_id)
            # 1. Check for Resize (Corners FIRST, then Edges)
            self.is_resizing = True
            # Corners
            if abs(rx - x1) < margin and abs(ry - y1) < margin: self.resize_corner = "nw"
            elif abs(rx - x2) < margin and abs(ry - y1) < margin: self.resize_corner = "ne"
            elif abs(rx - x1) < margin and abs(ry - y2) < margin: self.resize_corner = "sw"
            elif abs(rx - x2) < margin and abs(ry - y2) < margin: self.resize_corner = "se"
            # Edges
            elif abs(ry - y1) < margin and x1 <= rx <= x2: self.resize_corner = "n"
            elif abs(ry - y2) < margin and x1 <= rx <= x2: self.resize_corner = "s"
            elif abs(rx - x1) < margin and y1 <= ry <= y2: self.resize_corner = "w"
            elif abs(rx - x2) < margin and y1 <= ry <= y2: self.resize_corner = "e"
            else:
                self.is_resizing = False
                self.resize_corner = None

            if self.is_resizing:
                self.drag_last_x, self.drag_last_y = rx, ry
                return

            # 2. Check for Move (Inside box)
            if x1 <= rx <= x2 and y1 <= ry <= y2:
                self.is_dragging = True
                self.drag_last_x, self.drag_last_y = rx, ry
            else:
                self.is_dragging = False

    def on_mouse_drag(self, event):
        if not self.original_image: return
        rx, ry = self.get_real_coords(event)
        dx = rx - self.drag_last_x
        dy = ry - self.drag_last_y
        
        if self.is_scaling_img:
            v_orig_w = self.original_image.width * self.zoom_level
            v_orig_h = self.original_image.height * self.zoom_level
            
            # Target scales
            new_sx = rx / v_orig_w if "e" in self.scale_corner or "se" in self.scale_corner else self.scaling_x
            new_sy = ry / v_orig_h if "s" in self.scale_corner or "se" in self.scale_corner else self.scaling_y
            
            new_sx = max(0.01, min(10.0, new_sx))
            new_sy = max(0.01, min(10.0, new_sy))
            
            if self.keep_aspect.get():
                # Proportional logic: find the dominant change if it's a corner, otherwise follow the single edge
                if self.scale_corner == "se":
                    new_sx = new_sy = max(new_sx, new_sy)
                elif self.scale_corner == "e":
                    new_sx = new_sy = new_sx
                elif self.scale_corner == "s":
                    new_sx = new_sy = new_sy
            
            if new_sx != self.scaling_x or new_sy != self.scaling_y:
                ratio_x = new_sx / self.scaling_x
                ratio_y = new_sy / self.scaling_y
                
                self._updating_vars = True
                self.rect_x.set(int(self.rect_x.get() * ratio_x))
                self.rect_y.set(int(self.rect_y.get() * ratio_y))
                self.rect_width.set(max(1, int(self.rect_width.get() * ratio_x)))
                self.rect_height.set(max(1, int(self.rect_height.get() * ratio_y)))
                self._updating_vars = False
                
                self.scaling_x = new_sx
                self.scaling_y = new_sy
                self.refresh_display()
        elif self.is_resizing and self.rect_id:
            vx1, vy1, vx2, vy2 = self.canvas.coords(self.rect_id)
            # Update the coordinate being dragged
            if "n" in self.resize_corner: vy1 = ry
            if "s" in self.resize_corner: vy2 = ry
            if "w" in self.resize_corner: vx1 = rx
            if "e" in self.resize_corner: vx2 = rx
            
            # Normalize and set directly to avoid intermediate trace conflict
            nx1, nx2 = (vx1, vx2) if vx1 < vx2 else (vx2, vx1)
            ny1, ny2 = (vy1, vy2) if vy1 < vy2 else (vy2, vy1)
            self.canvas.coords(self.rect_id, nx1, ny1, nx2, ny2)
            self.update_vars_from_rect()
            
        elif self.is_dragging:
            self.canvas.move(self.rect_id, dx, dy)
            self.update_vars_from_rect()
        
        self.drag_last_x, self.drag_last_y = rx, ry

    def on_mouse_up(self, event):
        self.is_dragging = self.is_resizing = self.is_scaling_img = False
        self.resize_corner = None
        self.scale_corner = None

    def on_mouse_hover(self, event):
        if not self.original_image: return
        rx, ry = self.get_real_coords(event)
        margin = 15
        
        # Scaling cursor (Image corners & edges)
        vw = self.original_image.width * self.scaling_x * self.zoom_level
        vh = self.original_image.height * self.scaling_y * self.zoom_level
        
        if abs(rx - vw) < margin and abs(ry - vh) < margin:
            self.canvas.config(cursor="size_nw_se") # Corner
            return
        elif abs(rx - vw) < margin and 0 <= ry <= vh:
            self.canvas.config(cursor="size_we")    # Right edge
            return
        elif abs(ry - vh) < margin and 0 <= rx <= vw:
            self.canvas.config(cursor="size_ns")    # Bottom edge
            return

        if self.is_full.get():
            self.canvas.config(cursor="")
            return

        try:
            if self.rect_id:
                x1, y1, x2, y2 = self.canvas.coords(self.rect_id)
                # Corner Cursors
                if (abs(rx - x1) < margin and abs(ry - y1) < margin) or (abs(rx - x2) < margin and abs(ry - y2) < margin):
                    self.canvas.config(cursor="size_nw_se")
                elif (abs(rx - x2) < margin and abs(ry - y1) < margin) or (abs(rx - x1) < margin and abs(ry - y2) < margin):
                    self.canvas.config(cursor="size_ne_sw")
                # Edge Cursors
                elif abs(ry - y1) < margin and x1 <= rx <= x2:
                    self.canvas.config(cursor="size_ns")
                elif abs(ry - y2) < margin and x1 <= rx <= x2:
                    self.canvas.config(cursor="size_ns")
                elif abs(rx - x1) < margin and y1 <= ry <= y2:
                    self.canvas.config(cursor="size_we")
                elif abs(rx - x2) < margin and y1 <= ry <= y2:
                    self.canvas.config(cursor="size_we")
                # Move Cursor
                elif x1 <= rx <= x2 and y1 <= ry <= y2:
                    self.canvas.config(cursor="fleur")
                else:
                    self.canvas.config(cursor="")
            else:
                self.canvas.config(cursor="")
        except: pass

    def on_mouse_wheel(self, event):
        if not self.original_image: return
        
        # Windows/macOS use event.delta, Linux uses event.num
        if event.num == 4: # Linux scroll up
            delta = 120
        elif event.num == 5: # Linux scroll down
            delta = -120
        else:
            delta = event.delta
            
        # Ctrl + Wheel = Zoom
        if event.state & 0x0004:
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        # Shift + Wheel = Horizontal Scroll
        elif event.state & 0x0001: 
            self.canvas.xview_scroll(int(-1 * (delta / 120)), "units")
        else:
            self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")

    def process_remove_bg(self):
        if not self.original_image:
            return
        
        # Disable button and show status
        self.btn_rembg.config(state='disabled')
        old_status = self.status_bar.cget("text")
        self.status_bar.config(text="AI is removing background... Please wait (1-3 seconds).", fg="blue")
        self.root.update_idletasks() # Force UI update

        def run_ai():
            try:
                # Execute AI removal
                # We work on original image to maintain quality
                output = remove(self.original_image)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.on_ai_complete(output, old_status))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("AI Error", f"Background removal failed: {e}"))
                self.root.after(0, lambda: self.btn_rembg.config(state='normal'))
                self.root.after(0, lambda: self.status_bar.config(text=old_status, fg="black"))

        import threading
        threading.Thread(target=run_ai, daemon=True).start()

    def on_ai_complete(self, new_image, old_status):
        self.original_image = new_image
        self.refresh_display()
        self.btn_rembg.config(state='normal')
        self.status_bar.config(text="Background removed successfully!", fg="green")
        # Revert status color after 3 seconds
        self.root.after(3000, lambda: self.status_bar.config(text=f"AI Result | {old_status}", fg="black"))

    # --- Action ---

    def crop_and_save(self):
        if not self.scaled_image: return
        
        if self.is_full.get():
            left, top = 0, 0
            right, bottom = self.scaled_image.width, self.scaled_image.height
        else:
            x, y = self.rect_x.get(), self.rect_y.get()
            w, h = self.rect_width.get(), self.rect_height.get()
            
            left, top = max(0, x), max(0, y)
            right, bottom = min(self.scaled_image.width, x + w), min(self.scaled_image.height, y + h)
        
        if right <= left or bottom <= top:
            messagebox.showerror("Error", "Selected area is empty or invalid.")
            return

        try:
            cropped = self.scaled_image.crop((left, top, right, bottom))
            self.show_save_preview(cropped)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare preview: {e}")

    def show_save_preview(self, cropped_image: Image.Image):
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Save Preview - Verify your edit")
        
        # --- Dynamic Sizing & Centering ---
        # Calculate ideal window size based on image aspect ratio
        img_w, img_h = cropped_image.width, cropped_image.height
        aspect = img_w / img_h
        
        # Target sizes
        target_pw, target_ph = 800, 600 # Base size defaults
        if aspect > 1.2: # Landscape
            target_pw = 850
            target_ph = int(850 / aspect) + 150 # +150 for header/footer
        elif aspect < 0.8: # Portrait
            target_ph = 700
            target_pw = int((700 - 150) * aspect) + 40
        
        # Clamp to reasonable screen limits
        pw = max(400, min(1000, target_pw))
        ph = max(450, min(800, target_ph))

        # Get parent window position to center
        self.root.update_idletasks()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        
        # Calculate new X/Y to center over parent
        px = rx + (rw // 2) - (pw // 2)
        py = ry + (rh // 2) - (ph // 2)
        
        preview_win.geometry(f"{pw}x{ph}+{max(0, px)}+{max(0, py)}")
        preview_win.transient(self.root)
        preview_win.grab_set()

        # UI Instructions
        header = tk.Frame(preview_win, pady=10)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="Preview: Does this look correct?", font=("Arial", 12, "bold")).pack()
        tk.Label(header, text=f"Resolution: {cropped_image.width} x {cropped_image.height} px", fg="gray").pack()

        # Image Display Area (Fit to window)
        container = tk.Frame(preview_win, bg="#333333")
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a scaled-down copy for preview only (keep aspect ratio)
        max_preview_w, max_preview_h = 760, 480
        preview_copy = cropped_image.copy()
        preview_copy.thumbnail((max_preview_w, max_preview_h), Image.Resampling.LANCZOS)
        
        self.preview_tk = ImageTk.PhotoImage(preview_copy)
        # Center the preview image in the dark container
        tk.Label(container, image=self.preview_tk, bg="#505050", relief=tk.RAISED).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Bottom Buttons
        footer = tk.Frame(preview_win, pady=15)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        btn_cancel = tk.Button(footer, text="Cancel / Re-Edit", command=preview_win.destroy, width=15)
        btn_cancel.pack(side=tk.LEFT, padx=50)

        def proceed_to_save():
            preview_win.destroy()
            self.execute_save(cropped_image)

        btn_confirm = tk.Button(footer, text="Confirm & Save...", command=proceed_to_save, 
                                bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15)
        btn_confirm.pack(side=tk.RIGHT, padx=50)

    def execute_save(self, image: Image.Image):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG files", "*.png")],
            initialfile="result.png"
        )
        if save_path:
            try:
                image.save(save_path)
                messagebox.showinfo("Success", f"Saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

def main():
    # If no arguments are provided, launch GUI
    if len(sys.argv) == 1:
        root = tk.Tk()
        app = PngCropperApp(root)
        root.mainloop()
        return

    # CLI Mode
    parser = argparse.ArgumentParser(description="Mini PNG Editor - CLI Mode")
    parser.add_argument("--input", "-i", required=True, help="Input image path")
    parser.add_argument("--output", "-o", help="Output image path (required unless using --info)")
    parser.add_argument("--info", action="store_true", help="Print image information as JSON and exit")
    parser.add_argument("--rembg", action="store_true", help="Remove background using AI")
    parser.add_argument("--crop", nargs=4, type=int, metavar=('X', 'Y', 'W', 'H'), help="Crop parameters: x y width height")
    parser.add_argument("--scale", nargs=2, type=int, metavar=('W', 'H'), help="Scale image to: width height")

    args = parser.parse_args()

    try:
        if not args.info and not args.output:
            parser.error("--output is required unless --info is specified")

        img = Image.open(args.input)

        if args.info:
            # Check if other processing arguments were provided to warn the user
            ignored = []
            if args.output: ignored.append("--output")
            if args.rembg: ignored.append("--rembg")
            if args.scale: ignored.append("--scale")
            if args.crop: ignored.append("--crop")
            
            if ignored:
                print(f"Warning: --info detected. The following arguments will be ignored: {', '.join(ignored)}", file=sys.stderr)

            info = {
                "width": img.width,
                "height": img.height,
                "mode": img.mode,
                "filename": os.path.basename(args.input)
            }
            print(json.dumps(info, indent=2))
            return

        img = img.convert("RGBA")

        # 1. AI Background Removal
        if args.rembg:
            if not HAS_REMBG:
                print("Error: AI (rembg) is not enabled or installed. Check settings.py.")
                sys.exit(1)
            print("Running AI Background Removal...")
            img = remove(img)

        # 2. Image Scaling (Data Scale)
        if args.scale:
            sw, sh = args.scale
            print(f"Scaling to {sw}x{sh}...")
            img = img.resize((sw, sh), Image.Resampling.LANCZOS)

        # 3. Cropping
        if args.crop:
            cx, cy, cw, ch = args.crop
            print(f"Cropping Area: X={cx}, Y={cy}, W={cw}, H={ch}...")
            left, top = max(0, cx), max(0, cy)
            right, bottom = min(img.width, cx + cw), min(img.height, cy + ch)
            
            if right <= left or bottom <= top:
                raise ValueError("Crop area is empty or invalid.")
            
            img = img.crop((left, top, right, bottom))

        # 4. Save
        img.save(args.output)
        print(f"Successfully saved to: {args.output}")

    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
