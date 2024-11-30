import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageEnhance, ImageTk, ImageOps

class PhotoEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editor")
        self.root.geometry("1000x800")  # Set window size
        self.root.config(bg="#FFFFFF")  # Set background color

        self.image = None
        self.original_image = None
        self.history = []  # Stack to hold previous image states

        # Creating UI elements
        self.frame = tk.Frame(root, bg="#C0C0C0")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Creating canvas for image display
        self.canvas_frame = tk.Frame(self.frame, bg="#FFFFFF")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#808080")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Button layouts
        self.button_frame = tk.Frame(self.frame, bg="#000000")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Defining buttons style
        self.button_style = {
            'font': ('Arial', 12, 'bold'),
            'bg': '#D3D3D3',
            'fg': '#000000',
            'relief': 'flat',
            'width': 20,
            'height': 2
        }

        # Buttons for various functionalities
        self.create_button(self.button_frame, "Open Image", self.open_image, 0, 0)
        self.create_button(self.button_frame, "Increase Brightness", self.increase_brightness, 0, 1)
        self.create_button(self.button_frame, "Increase Contrast", self.increase_contrast, 0, 2)
        self.create_button(self.button_frame, "Rotate 90°", self.rotate_image, 0, 3)
        self.create_button(self.button_frame, "Grayscale", self.convert_grayscale, 0, 4)
        self.create_button(self.button_frame, "Flip Image", self.flip_image, 0, 5)
        self.create_button(self.button_frame, "Crop Image", self.crop_image, 1, 1)
        self.create_button(self.button_frame, "Undo", self.undo, 1, 2)
        self.create_button(self.button_frame, "Reset Image", self.reset_image, 1, 3)
        self.create_button(self.button_frame, "Save Image", self.save_image, 1, 4)

    def create_button(self, parent, text, command, row, col):
        button = tk.Button(parent, text=text, command=command, **self.button_style)
        button.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        return button

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[("Image Files", "*.png"), ("Image Files", "*.jpg"), ("Image Files", "*.jpeg"),
                      ("Image Files", "*.bmp"), ("Image Files", "*.gif")]
        )

        if file_path:
            try:
                self.image = Image.open(file_path)
                self.original_image = self.image.copy()

                self.history.clear()
                self.history.append(self.image.copy())

                self.resize_image_to_fit_canvas()
                self.display_image()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {e}")
        else:
            messagebox.showwarning("Warning", "No file selected")

    def resize_image_to_fit_canvas(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        self.image.thumbnail((canvas_width, canvas_height))
        self.display_image()

    def display_image(self):
        if self.image:
            try:
                tk_image = ImageTk.PhotoImage(self.image)

                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

                self.canvas.image = tk_image
            except Exception as e:
                messagebox.showerror("Error", f"Failed to display image: {e}")

    def increase_brightness(self):
        if self.image:
            self.save_state()  
            enhancer = ImageEnhance.Brightness(self.image)
            self.image = enhancer.enhance(1.2) 
            self.display_image()
        else:
            messagebox.showwarning("Warning", "No image loaded")

    def increase_contrast(self):
        if self.image:
            self.save_state()  
            enhancer = ImageEnhance.Contrast(self.image)
            self.image = enhancer.enhance(1.3)  
            self.display_image()
        else:
            messagebox.showwarning("Warning", "No image loaded")

    def rotate_image(self):
        if self.image:
            self.save_state()  
            self.image = self.image.rotate(90, expand=True)  
            self.resize_image_to_fit_canvas()
            self.display_image()
        else:
            messagebox.showwarning("Warning", "No image loaded")

    def convert_grayscale(self):
        if self.image:
            self.save_state()  
            self.image = self.image.convert("L") 
            self.resize_image_to_fit_canvas()
            self.display_image()
        else:
            messagebox.showwarning("Warning", "No image loaded")

    def flip_image(self):
        if self.image:
            self.save_state()  
            self.image = ImageOps.mirror(self.image)  
            self.resize_image_to_fit_canvas()
            self.display_image()
        else:
            messagebox.showwarning("Warning", "No image loaded")

    def crop_image(self):
        if self.image:
            self.save_state()  
            self.canvas.bind("<ButtonPress-1>", self.on_crop_start)
            self.canvas.bind("<B1-Motion>", self.on_crop_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_crop_end)
        else:
            messagebox.showwarning("Warning", "No image loaded")

    def on_crop_start(self, event):
        self.crop_start = (event.x, event.y)

    def on_crop_drag(self, event):
        if self.crop_start:
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)

            self.crop_rect = self.canvas.create_rectangle(
                self.crop_start[0], self.crop_start[1], event.x, event.y, outline="red", width=2
            )

    def on_crop_end(self, event):
        if self.crop_start:
            crop_end = (event.x, event.y)
            crop_box = (
                min(self.crop_start[0], crop_end[0]),
                min(self.crop_start[1], crop_end[1]),
                max(self.crop_start[0], crop_end[0]),
                max(self.crop_start[1], crop_end[1]),
            )
            self.image = self.image.crop(crop_box)  
            self.resize_image_to_fit_canvas()
            self.display_image()
            self.canvas.delete(self.crop_rect)  
            self.crop_start = None
            self.crop_rect = None

    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()  
            self.resize_image_to_fit_canvas()
            self.display_image()
        else:
            messagebox.showwarning("Warning", "No image loaded")

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=".jpg",
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
            )
            if file_path:
                try:
                    self.image.save(file_path)  
                    messagebox.showinfo("Success", f"Image saved as {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")
        else:
            messagebox.showwarning("Warning", "No image to save")

    def undo(self):
        if len(self.history) > 1:  
            self.history.pop()  
            self.image = self.history[-1] 
            self.display_image()
        else:
            messagebox.showwarning("Warning", "No action to undo")

    def save_state(self):
        if self.image:
            self.history.append(self.image.copy())  


root = tk.Tk()
app = PhotoEditorApp(root)
root.mainloop()
