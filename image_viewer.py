import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer using Tkinter")
        self.root.geometry("800x600")
        
        # Image list and current index
        self.image_paths = []
        self.current_index = 0
        self.current_image = None # To hold reference to prevent garbage collection
        
        self.setup_ui()
        
    def setup_ui(self):
        # Image display area
        self.image_label = tk.Label(self.root, text="Select a folder to view images", bg="gray")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Next Button
        self.btn_next = tk.Button(self.button_frame, text="Next", command=self.next_image, state=tk.DISABLED, width=10)
        self.btn_next.pack(side=tk.RIGHT, padx=20)
        
        # Exit Button
        self.btn_exit = tk.Button(self.button_frame, text="Exit", command=self.root.quit, width=10)
        self.btn_exit.pack(side=tk.RIGHT, padx=20)

        # Previous Button
        self.btn_prev = tk.Button(self.button_frame, text="Previous", command=self.prev_image, state=tk.DISABLED, width=10)
        self.btn_prev.pack(side=tk.RIGHT, padx=20)
        
        # Select Folder Button
        self.btn_select = tk.Button(self.button_frame, text="Select Folder", command=self.select_folder, width=15)
        self.btn_select.pack(side=tk.LEFT, padx=20)

        # Bind resize event
        self.root.bind("<Configure>", self.on_resize)
        
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.load_images(folder_selected)

    def load_images(self, folder_path):
        self.image_paths = []
        try:
            for file in os.listdir(folder_path):
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    self.image_paths.append(os.path.join(folder_path, file))
        except OSError as e:
            messagebox.showerror("Error", f"Could not access folder: {e}")
            return

        if not self.image_paths:
            messagebox.showinfo("No Images", "No supported images found in the selected folder.")
            self.image_label.config(image='', text="No images found")
            self.current_index = 0
            self.update_button_states()
            return

        self.current_index = 0
        self.show_image(self.current_index)
        self.update_button_states()
        
    def show_image(self, index):
        if not self.image_paths or index < 0 or index >= len(self.image_paths):
            return
            
        image_path = self.image_paths[index]
        try:
            img = Image.open(image_path)
            
            # Resize image to fit window while maintaining aspect ratio
            # Get current window size (or default if not yet rendered)
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()
            
            # Adjust for button frame
            display_height = win_height - self.button_frame.winfo_height() - 20 
            
            if display_height <= 0: display_height = 100 # Fallback
            if win_width <= 0: win_width = 100 # Fallback
            
            # Calculate resize ratio
            img_width, img_height = img.size
            ratio = min(win_width / img_width, display_height / img_height)
            
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            if new_width > 0 and new_height > 0:
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, text="")
            self.root.title(f"Image Viewer - {os.path.basename(image_path)} ({index + 1}/{len(self.image_paths)})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def on_resize(self, event):
        # Prevent resizing on every tiny event, maybe check if size actually changed or just reload current image
        # This event is triggered for all widgets, check if it's main window
        if event.widget == self.root and self.image_paths:
             # Basic debounce or check could go here, but for now just show_image
             # We need to use 'self.root.after_cancel' pattern for proper debounce if laggy
             # For simplicity, let's just recall show_image
             self.show_image(self.current_index)

    def next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.show_image(self.current_index)
            self.update_button_states()
        
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)
            self.update_button_states()

    def update_button_states(self):
        has_images = len(self.image_paths) > 0
        
        if not has_images:
            self.btn_next.config(state=tk.DISABLED)
            self.btn_prev.config(state=tk.DISABLED)
            return
            
        if self.current_index == 0:
             self.btn_prev.config(state=tk.DISABLED)
        else:
             self.btn_prev.config(state=tk.NORMAL)
             
        if self.current_index == len(self.image_paths) - 1:
            self.btn_next.config(state=tk.DISABLED)
        else:
            self.btn_next.config(state=tk.NORMAL)

if __name__ == "__main__":
    should_run = True
    try:
        import PIL
    except ImportError:
        print("Pillow library not found. Please install it using 'pip install Pillow'")
        should_run = False
        
    if should_run:
        root = tk.Tk()
        app = ImageViewerApp(root)
        root.mainloop()
