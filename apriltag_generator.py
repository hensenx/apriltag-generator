"""
AprilTag Generator Application
A GUI application for generating single AprilTags or arrays of AprilTags.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import os


class AprilTagGenerator:
    """Generates AprilTag images"""
    
    # AprilTag family patterns (tag36h11 family - simplified subset)
    TAG36H11_PATTERNS = {
        0: np.array([
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,0,1],
            [1,0,1,0,1,0,0,1],
            [1,0,1,1,0,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1]
        ]),
        1: np.array([
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,0,1],
            [1,0,1,0,1,0,0,1],
            [1,0,1,1,1,0,0,1],
            [1,0,0,0,1,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1]
        ]),
        2: np.array([
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1]
        ]),
        3: np.array([
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1]
        ]),
        4: np.array([
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,0,0,0,1,0,1],
            [1,0,0,0,0,1,0,1],
            [1,1,1,1,1,1,1,1]
        ]),
        5: np.array([
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,1],
            [1,1,1,1,1,1,1,1]
        ]),
    }
    
    @staticmethod
    def generate_tag(tag_id, size=200, border=1):
        """
        Generate a single AprilTag
        
        Args:
            tag_id: ID of the tag to generate
            size: Size of the tag in pixels
            border: Border size in units (1 = one cell width)
        
        Returns:
            PIL Image object
        """
        # Get pattern or use modulo to wrap around
        pattern_id = tag_id % len(AprilTagGenerator.TAG36H11_PATTERNS)
        pattern = AprilTagGenerator.TAG36H11_PATTERNS[pattern_id].copy()
        
        # Modify pattern slightly based on tag_id to create variations
        if tag_id >= len(AprilTagGenerator.TAG36H11_PATTERNS):
            variations = tag_id // len(AprilTagGenerator.TAG36H11_PATTERNS)
            # Flip some internal bits (not border) based on variation
            if variations % 2 == 1:
                pattern[2:6, 2:6] = 1 - pattern[2:6, 2:6]
        
        # Calculate cell size
        pattern_size = pattern.shape[0]
        total_size = pattern_size + (2 * border)
        cell_size = size // total_size
        
        # Create image with border
        img_size = cell_size * total_size
        img = Image.new('L', (img_size, img_size), 255)
        draw = ImageDraw.Draw(img)
        
        # Draw the pattern
        for i in range(pattern_size):
            for j in range(pattern_size):
                if pattern[i, j] == 1:
                    x0 = (j + border) * cell_size
                    y0 = (i + border) * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    draw.rectangle([x0, y0, x1, y1], fill=0)
        
        return img
    
    @staticmethod
    def generate_tag_array(tag_ids, rows, cols, tag_size=200, spacing=50, 
                          border=1, add_labels=True):
        """
        Generate an array of AprilTags (checkerboard style)
        
        Args:
            tag_ids: List of tag IDs or starting ID
            rows: Number of rows
            cols: Number of columns
            tag_size: Size of each tag in pixels
            spacing: Spacing between tags in pixels
            border: Border size for each tag
            add_labels: Whether to add ID labels below each tag
        
        Returns:
            PIL Image object
        """
        # Generate list of tag IDs if only starting ID provided
        if isinstance(tag_ids, int):
            tag_ids = list(range(tag_ids, tag_ids + rows * cols))
        
        # Calculate dimensions
        label_height = 30 if add_labels else 0
        total_tag_height = tag_size + label_height
        
        canvas_width = cols * tag_size + (cols - 1) * spacing + 2 * spacing
        canvas_height = rows * total_tag_height + (rows - 1) * spacing + 2 * spacing
        
        # Create canvas
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        draw = ImageDraw.Draw(canvas)
        
        # Try to load a font for labels
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Place tags
        idx = 0
        for row in range(rows):
            for col in range(cols):
                if idx < len(tag_ids):
                    tag_id = tag_ids[idx]
                    
                    # Generate tag
                    tag = AprilTagGenerator.generate_tag(tag_id, tag_size, border)
                    
                    # Calculate position
                    x = spacing + col * (tag_size + spacing)
                    y = spacing + row * (total_tag_height + spacing)
                    
                    # Paste tag
                    canvas.paste(tag, (x, y))
                    
                    # Add label
                    if add_labels:
                        label = f"ID: {tag_id}"
                        # Get text size
                        bbox = draw.textbbox((0, 0), label, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_x = x + (tag_size - text_width) // 2
                        text_y = y + tag_size + 5
                        draw.text((text_x, text_y), label, fill='black', font=font)
                    
                    idx += 1
        
        return canvas


class AprilTagGUI:
    """GUI for AprilTag Generator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AprilTag Generator")
        self.root.geometry("600x650")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.single_tab = ttk.Frame(self.notebook)
        self.batch_tab = ttk.Frame(self.notebook)
        self.array_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.single_tab, text='Single Tag')
        self.notebook.add(self.batch_tab, text='Batch Generate')
        self.notebook.add(self.array_tab, text='Tag Array')
        
        self.setup_single_tab()
        self.setup_batch_tab()
        self.setup_array_tab()
    
    def setup_single_tab(self):
        """Setup the single tag generation tab"""
        frame = ttk.LabelFrame(self.single_tab, text="Single AprilTag Settings", 
                              padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tag ID
        ttk.Label(frame, text="Tag ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.single_id = ttk.Spinbox(frame, from_=0, to=1000, width=20)
        self.single_id.set(0)
        self.single_id.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Tag Size
        ttk.Label(frame, text="Tag Size (pixels):").grid(row=1, column=0, 
                                                         sticky='w', pady=5)
        self.single_size = ttk.Spinbox(frame, from_=100, to=1000, increment=50, 
                                      width=20)
        self.single_size.set(400)
        self.single_size.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Border
        ttk.Label(frame, text="Border Width:").grid(row=2, column=0, 
                                                    sticky='w', pady=5)
        self.single_border = ttk.Spinbox(frame, from_=0, to=3, width=20)
        self.single_border.set(1)
        self.single_border.grid(row=2, column=1, sticky='ew', pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Preview and Generate buttons
        button_frame = ttk.Frame(self.single_tab)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Preview", 
                  command=self.preview_single).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Generate & Save", 
                  command=self.generate_single).pack(side='left', padx=5)
        
        # Info label
        info_text = ("AprilTags are fiducial markers used for camera pose estimation.\n"
                    "Tag ID: Unique identifier for the marker (0-1000)\n"
                    "Tag Size: Output image size in pixels\n"
                    "Border: White border around the tag (recommended: 1)")
        info_label = ttk.Label(self.single_tab, text=info_text, 
                              justify='left', wraplength=550)
        info_label.pack(padx=10, pady=10)
    
    def setup_batch_tab(self):
        """Setup the batch tag generation tab"""
        frame = ttk.LabelFrame(self.batch_tab, text="Batch Generation Settings", 
                              padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Start Tag ID
        ttk.Label(frame, text="Start Tag ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.batch_start_id = ttk.Spinbox(frame, from_=0, to=1000, width=20)
        self.batch_start_id.set(0)
        self.batch_start_id.grid(row=0, column=1, sticky='ew', pady=5)
        
        # End Tag ID
        ttk.Label(frame, text="End Tag ID:").grid(row=1, column=0, sticky='w', pady=5)
        self.batch_end_id = ttk.Spinbox(frame, from_=0, to=1000, width=20)
        self.batch_end_id.set(9)
        self.batch_end_id.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Tag Size
        ttk.Label(frame, text="Tag Size (pixels):").grid(row=2, column=0, 
                                                         sticky='w', pady=5)
        self.batch_size = ttk.Spinbox(frame, from_=100, to=1000, increment=50, 
                                     width=20)
        self.batch_size.set(400)
        self.batch_size.grid(row=2, column=1, sticky='ew', pady=5)
        
        # Border
        ttk.Label(frame, text="Border Width:").grid(row=3, column=0, 
                                                    sticky='w', pady=5)
        self.batch_border = ttk.Spinbox(frame, from_=0, to=3, width=20)
        self.batch_border.set(1)
        self.batch_border.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Output Directory
        ttk.Label(frame, text="Output Directory:").grid(row=4, column=0, 
                                                        sticky='w', pady=5)
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=4, column=1, sticky='ew', pady=5)
        
        self.batch_output_dir = tk.StringVar(value=os.getcwd())
        ttk.Entry(dir_frame, textvariable=self.batch_output_dir).pack(
            side='left', fill='x', expand=True)
        ttk.Button(dir_frame, text="Browse...", 
                  command=self.browse_output_dir).pack(side='left', padx=(5, 0))
        
        frame.columnconfigure(1, weight=1)
        
        # Progress bar
        self.batch_progress = ttk.Progressbar(self.batch_tab, mode='determinate')
        self.batch_progress.pack(fill='x', padx=10, pady=5)
        
        # Status label
        self.batch_status = ttk.Label(self.batch_tab, text="Ready to generate tags")
        self.batch_status.pack(padx=10, pady=5)
        
        # Generate button
        button_frame = ttk.Frame(self.batch_tab)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Generate All Tags", 
                  command=self.generate_batch).pack(side='left', padx=5)
        
        # Info label
        info_text = ("Batch generate multiple individual AprilTag files.\n"
                    "Each tag will be saved as a separate PNG file:\n"
                    "apriltag_0.png, apriltag_1.png, etc.\n"
                    "Perfect for creating a complete set of tracking markers.")
        info_label = ttk.Label(self.batch_tab, text=info_text, 
                              justify='left', wraplength=550)
        info_label.pack(padx=10, pady=10)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            initialdir=self.batch_output_dir.get(),
            title="Select Output Directory"
        )
        if directory:
            self.batch_output_dir.set(directory)
    
    def generate_batch(self):
        """Generate batch of single tags"""
        try:
            start_id = int(self.batch_start_id.get())
            end_id = int(self.batch_end_id.get())
            size = int(self.batch_size.get())
            border = int(self.batch_border.get())
            output_dir = self.batch_output_dir.get()
            
            # Validate inputs
            if start_id > end_id:
                messagebox.showerror("Error", "Start ID must be less than or equal to End ID")
                return
            
            if not os.path.exists(output_dir):
                messagebox.showerror("Error", "Output directory does not exist")
                return
            
            # Calculate total tags
            total_tags = end_id - start_id + 1
            
            # Confirm with user
            if total_tags > 50:
                confirm = messagebox.askyesno(
                    "Confirm Batch Generation",
                    f"Generate {total_tags} tag files?\n"
                    f"This may take a moment."
                )
                if not confirm:
                    return
            
            # Setup progress bar
            self.batch_progress['maximum'] = total_tags
            self.batch_progress['value'] = 0
            
            # Generate tags
            for i, tag_id in enumerate(range(start_id, end_id + 1)):
                # Update status
                self.batch_status.config(
                    text=f"Generating tag {tag_id} ({i+1}/{total_tags})..."
                )
                self.root.update()
                
                # Generate tag
                img = AprilTagGenerator.generate_tag(tag_id, size, border)
                
                # Save tag
                filename = os.path.join(output_dir, f"apriltag_{tag_id}.png")
                img.save(filename)
                
                # Update progress
                self.batch_progress['value'] = i + 1
                self.root.update()
            
            # Complete
            self.batch_status.config(text=f"Successfully generated {total_tags} tags!")
            messagebox.showinfo(
                "Success",
                f"Generated {total_tags} AprilTag files in:\n{output_dir}"
            )
            
        except Exception as e:
            self.batch_status.config(text="Error occurred")
            messagebox.showerror("Error", f"Failed to generate batch: {str(e)}")

    
    def setup_array_tab(self):
        """Setup the tag array generation tab"""
        frame = ttk.LabelFrame(self.array_tab, text="Tag Array Settings", 
                              padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Starting Tag ID
        ttk.Label(frame, text="Starting Tag ID:").grid(row=0, column=0, 
                                                       sticky='w', pady=5)
        self.array_start_id = ttk.Spinbox(frame, from_=0, to=1000, width=20)
        self.array_start_id.set(0)
        self.array_start_id.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Rows
        ttk.Label(frame, text="Rows:").grid(row=1, column=0, sticky='w', pady=5)
        self.array_rows = ttk.Spinbox(frame, from_=1, to=20, width=20)
        self.array_rows.set(3)
        self.array_rows.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Columns
        ttk.Label(frame, text="Columns:").grid(row=2, column=0, sticky='w', pady=5)
        self.array_cols = ttk.Spinbox(frame, from_=1, to=20, width=20)
        self.array_cols.set(4)
        self.array_cols.grid(row=2, column=1, sticky='ew', pady=5)
        
        # Tag Size
        ttk.Label(frame, text="Tag Size (pixels):").grid(row=3, column=0, 
                                                         sticky='w', pady=5)
        self.array_size = ttk.Spinbox(frame, from_=50, to=500, increment=25, 
                                     width=20)
        self.array_size.set(200)
        self.array_size.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Spacing
        ttk.Label(frame, text="Spacing (pixels):").grid(row=4, column=0, 
                                                        sticky='w', pady=5)
        self.array_spacing = ttk.Spinbox(frame, from_=0, to=200, increment=10, 
                                        width=20)
        self.array_spacing.set(50)
        self.array_spacing.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Border
        ttk.Label(frame, text="Border Width:").grid(row=5, column=0, 
                                                    sticky='w', pady=5)
        self.array_border = ttk.Spinbox(frame, from_=0, to=3, width=20)
        self.array_border.set(1)
        self.array_border.grid(row=5, column=1, sticky='ew', pady=5)
        
        # Add Labels checkbox
        self.array_labels = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Add ID Labels", 
                       variable=self.array_labels).grid(row=6, column=0, 
                                                        columnspan=2, pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Preview and Generate buttons
        button_frame = ttk.Frame(self.array_tab)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Preview", 
                  command=self.preview_array).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Generate & Save", 
                  command=self.generate_array).pack(side='left', padx=5)
        
        # Info label
        info_text = ("Generate a grid/array of AprilTags.\n"
                    "Perfect for creating calibration boards or tracking patterns.\n"
                    "Tags will be numbered sequentially from the starting ID.")
        info_label = ttk.Label(self.array_tab, text=info_text, 
                              justify='left', wraplength=550)
        info_label.pack(padx=10, pady=10)
    
    def preview_single(self):
        """Preview single tag"""
        try:
            tag_id = int(self.single_id.get())
            size = int(self.single_size.get())
            border = int(self.single_border.get())
            
            img = AprilTagGenerator.generate_tag(tag_id, size, border)
            img.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview tag: {str(e)}")
    
    def generate_single(self):
        """Generate and save single tag"""
        try:
            tag_id = int(self.single_id.get())
            size = int(self.single_size.get())
            border = int(self.single_border.get())
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=f"apriltag_{tag_id}.png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if filename:
                img = AprilTagGenerator.generate_tag(tag_id, size, border)
                img.save(filename)
                messagebox.showinfo("Success", 
                                   f"Tag {tag_id} saved to:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate tag: {str(e)}")
    
    def preview_array(self):
        """Preview tag array"""
        try:
            start_id = int(self.array_start_id.get())
            rows = int(self.array_rows.get())
            cols = int(self.array_cols.get())
            size = int(self.array_size.get())
            spacing = int(self.array_spacing.get())
            border = int(self.array_border.get())
            labels = self.array_labels.get()
            
            img = AprilTagGenerator.generate_tag_array(
                start_id, rows, cols, size, spacing, border, labels
            )
            img.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview array: {str(e)}")
    
    def generate_array(self):
        """Generate and save tag array"""
        try:
            start_id = int(self.array_start_id.get())
            rows = int(self.array_rows.get())
            cols = int(self.array_cols.get())
            size = int(self.array_size.get())
            spacing = int(self.array_spacing.get())
            border = int(self.array_border.get())
            labels = self.array_labels.get()
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=f"apriltag_array_{rows}x{cols}.png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if filename:
                img = AprilTagGenerator.generate_tag_array(
                    start_id, rows, cols, size, spacing, border, labels
                )
                img.save(filename)
                messagebox.showinfo("Success", 
                                   f"Tag array ({rows}x{cols}) saved to:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate array: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AprilTagGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
