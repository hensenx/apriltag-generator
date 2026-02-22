"""
AprilTag Generator - Production Ready
A GUI application for generating AprilTags with rectangular or circular styles.
Uses official tag36h11 codes from AprilRobotics repository (all 587 codes).

Supports:
- Rectangular AprilTags (standard square format)
- Circular AprilTags (with smooth rounded edges)
- Single tag generation
- Batch generation
- Array/grid layouts
- DPI-based sizing (cm/inches + DPI = pixels)
- PNG, SVG, and PDF export formats
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageDraw
import os
from pathlib import Path
from tag36h11_complete import Tag36h11


class AprilTagGenerator:
    """Generates AprilTag images using official tag36h11 codes"""
    
    @staticmethod
    def _render_pattern_rectangular(pattern, size):
        """
        Render a tag pattern as rectangular image.
        
        Args:
            pattern: 10x10 numpy array (1=black, 0=white)
            size: Output image size in pixels
            
        Returns:
            PIL Image (grayscale)
        """
        pattern_size = pattern.shape[0]
        cell_size = size // pattern_size
        img_size = cell_size * pattern_size
        
        img = Image.new('L', (img_size, img_size), 255)
        draw = ImageDraw.Draw(img)
        
        for i in range(pattern_size):
            for j in range(pattern_size):
                if pattern[i, j] == 1:  # 1 in official pattern = black pixel
                    x0 = j * cell_size
                    y0 = i * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    draw.rectangle([x0, y0, x1, y1], fill=0)
        
        if img_size != size:
            img = img.resize((size, size), Image.NEAREST)
        
        return img
    
    @staticmethod
    def _render_pattern_circular(pattern, size):
        """
        Render a tag pattern as circular image (no alpha - rendered on white background).
        
        Args:
            pattern: 10x10 numpy array (1=black, 0=white)
            size: Output image size in pixels
            
        Returns:
            PIL Image (grayscale, no alpha)
        """
        # Create image with padding for circle
        img = Image.new('L', (size, size), 255)
        draw = ImageDraw.Draw(img)
        
        # Circle parameters
        margin = 2
        pattern_size = pattern.shape[0]
        cell_size = (size - 2 * margin) / pattern_size
        center_x = size / 2
        center_y = size / 2
        radius = (size - 2 * margin) / 2
        
        # Render each cell in circular region
        for i in range(pattern_size):
            for j in range(pattern_size):
                if pattern[i, j] == 1:  # Black pixel
                    # Calculate cell center
                    cell_x = margin + (j + 0.5) * cell_size
                    cell_y = margin + (i + 0.5) * cell_size
                    
                    # Check if cell is within circle
                    dist = np.sqrt((cell_x - center_x)**2 + (cell_y - center_y)**2)
                    if dist <= radius:
                        # Draw black rectangle for this cell
                        x0 = int(margin + j * cell_size)
                        y0 = int(margin + i * cell_size)
                        x1 = int(x0 + cell_size)
                        y1 = int(y0 + cell_size)
                        draw.rectangle([x0, y0, x1, y1], fill=0)
        
        return img
    
    @staticmethod
    def generate_tag(tag_id, size=200, style='rectangular', circle_x=None):
        """
        Generate a single AprilTag using official tag36h11 code.
        
        Args:
            tag_id: ID of the tag to generate (0-586)
            size: Size of the full tag in pixels (includes white border)
            style: 'rectangular' or 'circular'
            circle_x: X coordinate for circular mask (alternative parameter)
            
        Returns:
            PIL Image object
        """
        # Support circle_x parameter as alias for circular style
        if circle_x is not None:
            style = 'circular'
        
        # Get official pattern
        pattern = Tag36h11.generate_tag_pattern(tag_id)
        
        # Render based on style
        if style == 'circular':
            return AprilTagGenerator._render_pattern_circular(pattern, size)
        else:
            return AprilTagGenerator._render_pattern_rectangular(pattern, size)
    
    @staticmethod
    def generate_tag_array(tag_ids, rows, cols, tag_size=200, spacing=50, 
                          style='rectangular', add_labels=True):
        """
        Generate an array of AprilTags in a grid layout.
        
        Args:
            tag_ids: List of tag IDs or starting ID
            rows: Number of rows
            cols: Number of columns
            tag_size: Size of each tag in pixels
            spacing: Spacing between tags in pixels
            style: 'rectangular' or 'circular'
            add_labels: Whether to add ID labels below each tag
            
        Returns:
            PIL Image object
        """
        # Convert starting ID to list
        if isinstance(tag_ids, int):
            tag_ids = list(range(tag_ids, tag_ids + rows * cols))
        
        # Calculate dimensions
        label_height = 30 if add_labels else 0
        total_tag_height = tag_size + label_height
        
        canvas_width = cols * tag_size + (cols - 1) * spacing + 2 * spacing
        canvas_height = rows * total_tag_height + (rows - 1) * spacing + 2 * spacing
        
        # Create canvas
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        
        # Place tags
        idx = 0
        for row in range(rows):
            for col in range(cols):
                if idx < len(tag_ids):
                    tag_id = tag_ids[idx]
                    
                    # Generate tag
                    tag = AprilTagGenerator.generate_tag(
                        tag_id, tag_size, style=style
                    )
                    
                    # Convert to RGB if needed
                    if tag.mode == 'RGBA':
                        tag_rgb = Image.new('RGB', tag.size, 'white')
                        tag_rgb.paste(tag, mask=tag.split()[3])
                        tag = tag_rgb
                    elif tag.mode == 'L':
                        tag = tag.convert('RGB')
                    
                    # Calculate position
                    x = spacing + col * (tag_size + spacing)
                    y = spacing + row * (total_tag_height + spacing)
                    
                    # Paste tag
                    canvas.paste(tag, (x, y))
                    
                    # Add label if requested
                    if add_labels:
                        draw = ImageDraw.Draw(canvas)
                        label = f"ID: {tag_id}"
                        label_y = y + tag_size + 5
                        draw.text((x + 5, label_y), label, fill='black')
                    
                    idx += 1
        
        return canvas


# Helper functions for DPI and SVG support
FULL_TAG_CELLS = 10
INNER_TAG_CELLS = 8  # excludes the outer white border ring


def size_without_border_to_full(size_value):
    """Convert requested size (excluding white border) to full tag size (including white border)."""
    return size_value * FULL_TAG_CELLS / INNER_TAG_CELLS


def size_full_to_without_border(size_value):
    """Convert full tag size (including white border) to size excluding white border."""
    return size_value * INNER_TAG_CELLS / FULL_TAG_CELLS


def calculate_pixels_from_physical(size_cm, dpi=72):
    """
    Convert physical size (cm) to pixels based on DPI.
    
    Args:
        size_cm: Size in centimeters
        dpi: Dots per inch (default 72)
    
    Returns:
        Size in pixels (integer)
    """
    inches = size_cm / 2.54
    pixels = int(inches * dpi)
    return pixels


def pixels_to_physical(pixels, dpi=72):
    """
    Convert pixels to physical size (cm) based on DPI.
    
    Args:
        pixels: Size in pixels
        dpi: Dots per inch (default 72)
    
    Returns:
        Size in centimeters (float)
    """
    inches = pixels / dpi
    cm = inches * 2.54
    return cm


def generate_svg_tag(tag_id, size_cm: float = 10.0, dpi=300, style='rectangular'):
    """
    Generate SVG (vector) AprilTag.
    
    Args:
        tag_id: Tag ID (0-586)
        size_cm: Size in centimeters
        dpi: Dots per inch
        style: 'rectangular' or 'circular'
    
    Returns:
        SVG string
    """
    from tag36h11_complete import Tag36h11
    
    # Convert size
    size_pixels = calculate_pixels_from_physical(size_cm, dpi)
    
    # Get pattern
    pattern = Tag36h11.generate_tag_pattern(tag_id)
    pattern_size = pattern.shape[0]
    cell_size = size_pixels / pattern_size
    
    # Start SVG with explicit physical dimensions for print-to-scale behavior
    size_cm_str = f"{size_cm:.6g}"
    svg_lines = [
        f'<svg width="{size_cm_str}cm" height="{size_cm_str}cm" viewBox="0 0 {size_pixels} {size_pixels}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect width="{size_pixels}" height="{size_pixels}" fill="white"/>'
    ]
    
    if style == 'circular':
        # Add circle background
        svg_lines.append(f'  <!-- Circular AprilTag {tag_id} (DPI: {dpi}) -->')
        margin = max(2, int(cell_size * 0.2))
        radius = (size_pixels - 2 * margin) / 2
        center = size_pixels / 2
    else:
        svg_lines.append(f'  <!-- Rectangular AprilTag {tag_id} (DPI: {dpi}) -->')
    
    # Add rectangles for black pixels
    for i in range(pattern_size):
        for j in range(pattern_size):
            if pattern[i, j] == 1:
                if style == 'circular':
                    # Check if within circle
                    cell_center_x = (j + 0.5) * cell_size
                    cell_center_y = (i + 0.5) * cell_size
                    dist = np.sqrt((cell_center_x - center)**2 + (cell_center_y - center)**2)
                    if dist <= radius:
                        x = int(j * cell_size)
                        y = int(i * cell_size)
                        w = int(cell_size)
                        h = int(cell_size)
                        svg_lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="black"/>')
                else:
                    x = int(j * cell_size)
                    y = int(i * cell_size)
                    w = int(cell_size)
                    h = int(cell_size)
                    svg_lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="black"/>')
    
    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)


def _require_reportlab_canvas():
    """Import reportlab canvas lazily for vector PDF exports."""
    try:
        from reportlab.pdfgen import canvas
        return canvas
    except ImportError as exc:
        raise ImportError("Vector PDF export requires reportlab. Install with: pip install reportlab") from exc


def _draw_pattern_on_pdf(pdf_canvas, pattern, origin_x_pt, origin_y_pt, tag_size_pt, style='rectangular'):
    """Draw one AprilTag pattern as vector rectangles onto a PDF canvas."""
    pattern_size = pattern.shape[0]
    cell_size_pt = tag_size_pt / pattern_size

    # White tag background
    pdf_canvas.setFillColorRGB(1, 1, 1)
    pdf_canvas.rect(origin_x_pt, origin_y_pt, tag_size_pt, tag_size_pt, stroke=0, fill=1)

    if style == 'circular':
        margin_pt = max(2.0, cell_size_pt * 0.2)
        radius_pt = (tag_size_pt - 2 * margin_pt) / 2
        center_x_pt = origin_x_pt + tag_size_pt / 2
        center_y_pt = origin_y_pt + tag_size_pt / 2
    else:
        center_x_pt = center_y_pt = radius_pt = margin_pt = None

    pdf_canvas.setFillColorRGB(0, 0, 0)
    for i in range(pattern_size):
        for j in range(pattern_size):
            if pattern[i, j] != 1:
                continue

            # Convert top-left pattern indexing to PDF bottom-left coordinates
            cell_x_pt = origin_x_pt + j * cell_size_pt
            cell_y_pt = origin_y_pt + tag_size_pt - (i + 1) * cell_size_pt

            if style == 'circular':
                cell_center_x_pt = origin_x_pt + (j + 0.5) * cell_size_pt
                cell_center_y_pt = origin_y_pt + tag_size_pt - (i + 0.5) * cell_size_pt
                dist_pt = np.sqrt((cell_center_x_pt - center_x_pt) ** 2 + (cell_center_y_pt - center_y_pt) ** 2)
                if dist_pt > radius_pt:
                    continue

            pdf_canvas.rect(cell_x_pt, cell_y_pt, cell_size_pt, cell_size_pt, stroke=0, fill=1)


def generate_pdf_tag(file_path, tag_id, size_cm: float = 10.0, style='rectangular'):
    """Generate a true vector PDF for a single AprilTag at a physical size."""
    canvas = _require_reportlab_canvas()
    points_per_cm = 72.0 / 2.54
    page_size_pt = size_cm * points_per_cm

    pdf = canvas.Canvas(file_path, pagesize=(page_size_pt, page_size_pt))
    pattern = Tag36h11.generate_tag_pattern(tag_id)
    _draw_pattern_on_pdf(pdf, pattern, 0.0, 0.0, page_size_pt, style=style)
    pdf.showPage()
    pdf.save()


def generate_pdf_array(file_path, start_id, rows, cols, tag_size_px=200, spacing_px=50,
                       style='rectangular', add_labels=True, dpi=72):
    """Generate a true vector PDF for a tag array, preserving current pixel-layout semantics."""
    canvas = _require_reportlab_canvas()

    label_height_px = 30 if add_labels else 0
    total_tag_height_px = tag_size_px + label_height_px
    canvas_width_px = cols * tag_size_px + (cols - 1) * spacing_px + 2 * spacing_px
    canvas_height_px = rows * total_tag_height_px + (rows - 1) * spacing_px + 2 * spacing_px

    points_per_px = 72.0 / dpi
    canvas_width_pt = canvas_width_px * points_per_px
    canvas_height_pt = canvas_height_px * points_per_px
    tag_size_pt = tag_size_px * points_per_px

    pdf = canvas.Canvas(file_path, pagesize=(canvas_width_pt, canvas_height_pt))

    # Full white page background
    pdf.setFillColorRGB(1, 1, 1)
    pdf.rect(0, 0, canvas_width_pt, canvas_height_pt, stroke=0, fill=1)

    idx = 0
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 9)

    for row in range(rows):
        for col in range(cols):
            tag_id = start_id + idx
            idx += 1
            if tag_id > 586:
                continue

            x_px = spacing_px + col * (tag_size_px + spacing_px)
            y_top_px = spacing_px + row * (total_tag_height_px + spacing_px)
            y_bottom_px = canvas_height_px - y_top_px - tag_size_px

            x_pt = x_px * points_per_px
            y_pt = y_bottom_px * points_per_px

            pattern = Tag36h11.generate_tag_pattern(tag_id)
            _draw_pattern_on_pdf(pdf, pattern, x_pt, y_pt, tag_size_pt, style=style)

            if add_labels:
                label_x_pt = (x_px + 5) * points_per_px
                label_baseline_from_top_px = y_top_px + tag_size_px + 15
                label_y_pt = (canvas_height_px - label_baseline_from_top_px) * points_per_px
                pdf.setFillColorRGB(0, 0, 0)
                pdf.drawString(label_x_pt, label_y_pt, f"ID: {tag_id}")

    pdf.showPage()
    pdf.save()


class AprilTagGUI:
    """GUI interface for AprilTag Generator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AprilTag Generator - Official Tag36h11")
        self.root.geometry("650x750")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create tabbed interface
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
        """Setup single tag generation tab"""
        frame = ttk.LabelFrame(self.single_tab, text="Single AprilTag", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tag ID
        ttk.Label(frame, text="Tag ID (0-586):").grid(row=0, column=0, sticky='w', pady=5)
        self.single_id = ttk.Spinbox(frame, from_=0, to=586, width=20)
        self.single_id.set(0)
        self.single_id.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Size mode selector
        ttk.Label(frame, text="Size Mode:").grid(row=1, column=0, sticky='w', pady=5)
        self.single_size_mode = ttk.Combobox(frame, values=['Pixels', 'Physical (cm) + DPI'], 
                                            state='readonly', width=17)
        self.single_size_mode.set('Pixels')
        self.single_size_mode.grid(row=1, column=1, sticky='ew', pady=5)
        self.single_size_mode.bind('<<ComboboxSelected>>', self._on_single_size_mode_changed)
        
        # Pixel size spinbox (shown by default)
        self.single_size_pixels_label = ttk.Label(frame, text="Size (pixels, no white border):")
        self.single_size_pixels_label.grid(row=2, column=0, sticky='w', pady=5)
        self.single_size_pixels = ttk.Spinbox(frame, from_=100, to=1000, increment=50, width=20)
        self.single_size_pixels.set(400)
        self.single_size_pixels.grid(row=2, column=1, sticky='ew', pady=5)
        self.single_size_pixels.bind('<KeyRelease>', self._update_single_display)
        
        # Physical size spinbox (hidden by default)
        self.single_size_cm_label = ttk.Label(frame, text="Size (cm, no white border):")
        self.single_size_cm = ttk.Spinbox(frame, from_=1, to=100, width=20)
        self.single_size_cm.set(10)
        self.single_size_cm.grid(row=2, column=0, sticky='w', pady=5)
        self.single_size_cm.grid(row=2, column=1, sticky='ew', pady=5)
        self.single_size_cm_label.grid_remove()
        self.single_size_cm.grid_remove()
        self.single_size_cm.bind('<KeyRelease>', self._update_single_display)
        
        # DPI selector (hidden by default)
        self.single_dpi_label = ttk.Label(frame, text="DPI:")
        self.single_dpi = ttk.Combobox(frame, values=['72 (Screen)', '96 (Web)', '150 (Photo)', '300 (Print)', '600 (High)'], 
                                      state='readonly', width=17)
        self.single_dpi.set('300 (Print)')
        self.single_dpi.grid(row=3, column=0, sticky='w', pady=5)
        self.single_dpi.grid(row=3, column=1, sticky='ew', pady=5)
        self.single_dpi_label.grid_remove()
        self.single_dpi.grid_remove()
        self.single_dpi.bind('<<ComboboxSelected>>', self._update_single_display)
        
        # Style
        self.single_style_label = ttk.Label(frame, text="Style:")
        self.single_style_label.grid(row=3, column=0, sticky='w', pady=5)
        self.single_style = ttk.Combobox(frame, values=['rectangular', 'circular'], 
                                        state='readonly', width=17)
        self.single_style.set('rectangular')
        self.single_style.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Export format
        self.single_format_label = ttk.Label(frame, text="Export Format:")
        self.single_format_label.grid(row=4, column=0, sticky='w', pady=5)
        self.single_format = ttk.Combobox(frame, values=['PNG (Raster)', 'SVG (Vector)', 'PDF (Print)'], 
                                         state='readonly', width=17)
        self.single_format.set('PNG (Raster)')
        self.single_format.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Real-world size display
        self.single_size_display_label = ttk.Label(frame, text="Real-world Size:")
        self.single_size_display_label.grid(row=5, column=0, sticky='w', pady=5)
        self.single_size_display = ttk.Label(frame, text="400px = 14.11cm (300 DPI)", 
                                             foreground='blue', font=('TkDefaultFont', 10, 'bold'))
        self.single_size_display.grid(row=5, column=1, sticky='w', pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Initial display update
        self._update_single_display()
        
        # Buttons
        btn_frame = ttk.Frame(self.single_tab)
        btn_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(btn_frame, text="Preview", command=self.preview_single).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Generate & Save", command=self.generate_single).pack(side='left', padx=5)
        
        # Info
        info = ttk.Label(self.single_tab, text="Generate a single AprilTag marker.\nSupports all 587 official tag36h11 codes.\nExport as PNG, SVG, or PDF.", 
                        justify='left', wraplength=600)
        info.pack(padx=10, pady=10)
    
    def _on_single_size_mode_changed(self, event=None):
        """Handle size mode change - toggle UI elements and update display"""
        mode = self.single_size_mode.get()
        
        if mode == 'Physical (cm) + DPI':
            # Switch to physical mode: hide pixels, show cm + DPI
            self.single_size_pixels_label.grid_remove()
            self.single_size_pixels.grid_remove()
            self.single_size_cm_label.grid(row=2, column=0, sticky='w', pady=5)
            self.single_size_cm.grid(row=2, column=1, sticky='ew', pady=5)
            self.single_dpi_label.grid(row=3, column=0, sticky='w', pady=5)
            self.single_dpi.grid(row=3, column=1, sticky='ew', pady=5)
            
            # Adjust other rows
            self.single_style_label.grid(row=4, column=0, sticky='w', pady=5)
            self.single_style.grid(row=4, column=1, sticky='ew', pady=5)
            self.single_format_label.grid(row=5, column=0, sticky='w', pady=5)
            self.single_format.grid(row=5, column=1, sticky='ew', pady=5)
            self.single_size_display_label.grid(row=6, column=0, sticky='w', pady=5)
            self.single_size_display.grid(row=6, column=1, sticky='w', pady=5)
        else:
            # Switch to pixel mode: show pixels, hide cm + DPI
            self.single_size_cm_label.grid_remove()
            self.single_size_cm.grid_remove()
            self.single_dpi_label.grid_remove()
            self.single_dpi.grid_remove()
            self.single_size_pixels_label.grid(row=2, column=0, sticky='w', pady=5)
            self.single_size_pixels.grid(row=2, column=1, sticky='ew', pady=5)
            
            # Adjust other rows back
            self.single_style_label.grid(row=3, column=0, sticky='w', pady=5)
            self.single_style.grid(row=3, column=1, sticky='ew', pady=5)
            self.single_format_label.grid(row=4, column=0, sticky='w', pady=5)
            self.single_format.grid(row=4, column=1, sticky='ew', pady=5)
            self.single_size_display_label.grid(row=5, column=0, sticky='w', pady=5)
            self.single_size_display.grid(row=5, column=1, sticky='w', pady=5)
        
        self._update_single_display()
    
    def _update_single_display(self, event=None):
        """Update real-world size display based on current mode and values"""
        try:
            mode = self.single_size_mode.get()
            
            if mode == 'Physical (cm) + DPI':
                # Physical mode: show cm, inches, DPI, and calculated export pixels
                size_cm = float(self.single_size_cm.get())
                dpi_str = self.single_dpi.get().split()[0]
                dpi = int(dpi_str)
                size_px = calculate_pixels_from_physical(size_cm, dpi)
                full_size_px = int(round(size_without_border_to_full(size_px)))
                inches = size_cm / 2.54
                self.single_size_display.config(
                    text=f"{size_cm:.1f}cm × {size_cm:.1f}cm ({inches:.2f}\" × {inches:.2f}\") @ {dpi} DPI = {size_px}px (+border → {full_size_px}px full)"
                )
            else:
                # Pixel mode: show pixels and convert to cm at 300 DPI reference
                size_px = int(self.single_size_pixels.get())
                size_cm = pixels_to_physical(size_px, dpi=300)
                full_size_px = int(round(size_without_border_to_full(size_px)))
                full_size_cm = pixels_to_physical(full_size_px, dpi=300)
                inches = size_cm / 2.54
                self.single_size_display.config(
                    text=f"{size_px}px = {size_cm:.2f}cm × {size_cm:.2f}cm ({inches:.2f}\" × {inches:.2f}\") @ 300 DPI (+border → {full_size_px}px / {full_size_cm:.2f}cm full)"
                )
        except (ValueError, IndexError):
            pass
    
    
    def setup_batch_tab(self):
        """Setup batch generation tab"""
        frame = ttk.LabelFrame(self.batch_tab, text="Batch Generation", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Start ID
        ttk.Label(frame, text="Start ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.batch_start = ttk.Spinbox(frame, from_=0, to=586, width=20)
        self.batch_start.set(0)
        self.batch_start.grid(row=0, column=1, sticky='ew', pady=5)
        
        # End ID
        ttk.Label(frame, text="End ID:").grid(row=1, column=0, sticky='w', pady=5)
        self.batch_end = ttk.Spinbox(frame, from_=0, to=586, width=20)
        self.batch_end.set(9)
        self.batch_end.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Size mode selector
        ttk.Label(frame, text="Size Mode:").grid(row=2, column=0, sticky='w', pady=5)
        self.batch_size_mode = ttk.Combobox(frame, values=['Pixels', 'Physical (cm) + DPI'], 
                                           state='readonly', width=17)
        self.batch_size_mode.set('Pixels')
        self.batch_size_mode.grid(row=2, column=1, sticky='ew', pady=5)
        self.batch_size_mode.bind('<<ComboboxSelected>>', self._on_batch_size_mode_changed)
        
        # Size (pixels) - default visible
        self.batch_size_pixels_label = ttk.Label(frame, text="Size (pixels, no white border):")
        self.batch_size_pixels_label.grid(row=3, column=0, sticky='w', pady=5)
        self.batch_size_pixels = ttk.Spinbox(frame, from_=100, to=1000, increment=50, width=20)
        self.batch_size_pixels.set(400)
        self.batch_size_pixels.grid(row=3, column=1, sticky='ew', pady=5)
        self.batch_size_pixels.bind('<KeyRelease>', self._update_batch_display)
        
        # Size (cm) - initially hidden
        self.batch_size_cm_label = ttk.Label(frame, text="Size (cm, no white border):")
        self.batch_size_cm = ttk.Spinbox(frame, from_=1, to=100, increment=1, width=20, format="%.1f")
        self.batch_size_cm.set(10.0)
        self.batch_size_cm.bind('<KeyRelease>', self._update_batch_display)
        # Grid then hide (to preserve grid info)
        self.batch_size_cm_label.grid(row=3, column=0, sticky='w', pady=5)
        self.batch_size_cm.grid(row=3, column=1, sticky='ew', pady=5)
        self.batch_size_cm_label.grid_remove()
        self.batch_size_cm.grid_remove()
        
        # DPI selector - initially hidden
        self.batch_dpi_label = ttk.Label(frame, text="DPI:")
        self.batch_dpi = ttk.Combobox(frame, values=['72 DPI (Screen)', '96 DPI (Web)', '150 DPI (Photo)', 
                                                     '300 DPI (Print)', '600 DPI (High-Res)'], 
                                     state='readonly', width=17)
        self.batch_dpi.set('300 DPI (Print)')
        self.batch_dpi.bind('<<ComboboxSelected>>', self._update_batch_display)
        # Grid then hide
        self.batch_dpi_label.grid(row=4, column=0, sticky='w', pady=5)
        self.batch_dpi.grid(row=4, column=1, sticky='ew', pady=5)
        self.batch_dpi_label.grid_remove()
        self.batch_dpi.grid_remove()
        
        # Style
        self.batch_style_label = ttk.Label(frame, text="Style:")
        self.batch_style_label.grid(row=4, column=0, sticky='w', pady=5)
        self.batch_style = ttk.Combobox(frame, values=['rectangular', 'circular'], 
                                       state='readonly', width=17)
        self.batch_style.set('rectangular')
        self.batch_style.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Export format
        self.batch_format_label = ttk.Label(frame, text="Export Format:")
        self.batch_format_label.grid(row=5, column=0, sticky='w', pady=5)
        self.batch_format = ttk.Combobox(frame, values=['PNG (Raster)', 'SVG (Vector)', 'PDF (Print)'], 
                                        state='readonly', width=17)
        self.batch_format.set('PNG (Raster)')
        self.batch_format.grid(row=5, column=1, sticky='ew', pady=5)
        
        # Output directory
        self.batch_dir_label = ttk.Label(frame, text="Output Dir:")
        self.batch_dir_label.grid(row=6, column=0, sticky='w', pady=5)
        self.batch_dir_frame = ttk.Frame(frame)
        self.batch_dir_frame.grid(row=6, column=1, sticky='ew', pady=5)
        self.batch_dir = tk.StringVar(value=os.getcwd())
        ttk.Entry(self.batch_dir_frame, textvariable=self.batch_dir).pack(side='left', fill='x', expand=True)
        ttk.Button(self.batch_dir_frame, text="Browse...", command=self.browse_dir).pack(side='left', padx=(5, 0))
        
        # Real-world size display
        self.batch_size_display_label = ttk.Label(frame, text="Real-world Size:")
        self.batch_size_display_label.grid(row=7, column=0, sticky='w', pady=5)
        self.batch_size_display = ttk.Label(frame, text="400 px per tag", 
                                            foreground='blue', font=('TkDefaultFont', 10, 'bold'))
        self.batch_size_display.grid(row=7, column=1, sticky='w', pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Initialize display
        self._update_batch_display()
        
        # Progress
        self.batch_progress = ttk.Progressbar(self.batch_tab, mode='determinate')
        self.batch_progress.pack(fill='x', padx=10, pady=5)
        
        self.batch_status = ttk.Label(self.batch_tab, text="Ready")
        self.batch_status.pack(padx=10, pady=5)
        
        # Button
        ttk.Button(self.batch_tab, text="Generate All", command=self.generate_batch).pack(padx=10, pady=5)
        
        # Info
        info = ttk.Label(self.batch_tab, text="Generate multiple individual tag files.\nEach saved as apriltag_N.png or apriltag_N.svg", 
                        justify='left', wraplength=600)
        info.pack(padx=10, pady=10)
    
    def _on_batch_size_mode_changed(self, event=None):
        """Handle batch size mode change - toggle UI elements and update display"""
        mode = self.batch_size_mode.get()
        
        if mode == 'Physical (cm) + DPI':
            # Switch to physical mode: hide pixels, show cm + DPI
            self.batch_size_pixels_label.grid_remove()
            self.batch_size_pixels.grid_remove()
            self.batch_size_cm_label.grid(row=3, column=0, sticky='w', pady=5)
            self.batch_size_cm.grid(row=3, column=1, sticky='ew', pady=5)
            self.batch_dpi_label.grid(row=4, column=0, sticky='w', pady=5)
            self.batch_dpi.grid(row=4, column=1, sticky='ew', pady=5)
            
            # Adjust other rows
            self.batch_style_label.grid(row=5, column=0, sticky='w', pady=5)
            self.batch_style.grid(row=5, column=1, sticky='ew', pady=5)
            self.batch_format_label.grid(row=6, column=0, sticky='w', pady=5)
            self.batch_format.grid(row=6, column=1, sticky='ew', pady=5)
            self.batch_dir_label.grid(row=7, column=0, sticky='w', pady=5)
            self.batch_dir_frame.grid(row=7, column=1, sticky='ew', pady=5)
            self.batch_size_display_label.grid(row=8, column=0, sticky='w', pady=5)
            self.batch_size_display.grid(row=8, column=1, sticky='w', pady=5)
        else:
            # Switch to pixel mode: show pixels, hide cm + DPI
            self.batch_size_cm_label.grid_remove()
            self.batch_size_cm.grid_remove()
            self.batch_dpi_label.grid_remove()
            self.batch_dpi.grid_remove()
            self.batch_size_pixels_label.grid(row=3, column=0, sticky='w', pady=5)
            self.batch_size_pixels.grid(row=3, column=1, sticky='ew', pady=5)
            
            # Adjust other rows back
            self.batch_style_label.grid(row=4, column=0, sticky='w', pady=5)
            self.batch_style.grid(row=4, column=1, sticky='ew', pady=5)
            self.batch_format_label.grid(row=5, column=0, sticky='w', pady=5)
            self.batch_format.grid(row=5, column=1, sticky='ew', pady=5)
            self.batch_dir_label.grid(row=6, column=0, sticky='w', pady=5)
            self.batch_dir_frame.grid(row=6, column=1, sticky='ew', pady=5)
            self.batch_size_display_label.grid(row=7, column=0, sticky='w', pady=5)
            self.batch_size_display.grid(row=7, column=1, sticky='w', pady=5)
        
        self._update_batch_display()
    
    def _update_batch_display(self, event=None):
        """Update batch size display based on current mode and values"""
        try:
            mode = self.batch_size_mode.get()
            
            if mode == 'Physical (cm) + DPI':
                # Physical mode: show cm, inches, DPI, and calculated export pixels
                size_cm = float(self.batch_size_cm.get())
                dpi_str = self.batch_dpi.get().split()[0]
                dpi = int(dpi_str)
                size_px = calculate_pixels_from_physical(size_cm, dpi)
                full_size_px = int(round(size_without_border_to_full(size_px)))
                inches = size_cm / 2.54
                self.batch_size_display.config(
                    text=f"{size_cm:.1f}cm × {size_cm:.1f}cm ({inches:.2f}\" × {inches:.2f}\") @ {dpi} DPI = {size_px}px/tag (+border → {full_size_px}px full)"
                )
            else:
                # Pixel mode: show pixels and convert to cm at 300 DPI reference
                size_px = int(self.batch_size_pixels.get())
                size_cm = pixels_to_physical(size_px, dpi=300)
                full_size_px = int(round(size_without_border_to_full(size_px)))
                full_size_cm = pixels_to_physical(full_size_px, dpi=300)
                inches = size_cm / 2.54
                self.batch_size_display.config(
                    text=f"{size_px}px/tag = {size_cm:.2f}cm × {size_cm:.2f}cm ({inches:.2f}\" × {inches:.2f}\") @ 300 DPI (+border → {full_size_px}px / {full_size_cm:.2f}cm full)"
                )
        except (ValueError, IndexError):
            pass
    
    def update_batch_size_display(self, event=None):
        """Legacy method - redirects to new _update_batch_display"""
        self._update_batch_display(event)
    
    def setup_array_tab(self):
        """Setup array generation tab"""
        frame = ttk.LabelFrame(self.array_tab, text="Tag Array", padding=20)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Start ID
        ttk.Label(frame, text="Start ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.array_start = ttk.Spinbox(frame, from_=0, to=586, width=20)
        self.array_start.set(0)
        self.array_start.grid(row=0, column=1, sticky='ew', pady=5)
        
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
        ttk.Label(frame, text="Tag Size (pixels, no white border):").grid(row=3, column=0, sticky='w', pady=5)
        self.array_size = ttk.Spinbox(frame, from_=50, to=500, increment=25, width=20)
        self.array_size.set(200)
        self.array_size.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Spacing
        ttk.Label(frame, text="Spacing (pixels):").grid(row=4, column=0, sticky='w', pady=5)
        self.array_spacing = ttk.Spinbox(frame, from_=0, to=200, increment=10, width=20)
        self.array_spacing.set(50)
        self.array_spacing.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Style
        ttk.Label(frame, text="Style:").grid(row=5, column=0, sticky='w', pady=5)
        self.array_style = ttk.Combobox(frame, values=['rectangular', 'circular'], 
                                       state='readonly', width=17)
        self.array_style.set('rectangular')
        self.array_style.grid(row=5, column=1, sticky='ew', pady=5)
        
        # Export format
        ttk.Label(frame, text="Export Format:").grid(row=6, column=0, sticky='w', pady=5)
        self.array_format = ttk.Combobox(frame, values=['PNG (Raster)', 'SVG (Vector)', 'PDF (Print)'], 
                                        state='readonly', width=17)
        self.array_format.set('PNG (Raster)')
        self.array_format.grid(row=6, column=1, sticky='ew', pady=5)
        
        # Labels checkbox
        self.array_labels = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Add ID Labels", variable=self.array_labels).grid(row=7, column=0, columnspan=2)
        
        # Real-world size display
        ttk.Label(frame, text="Dimensions:").grid(row=8, column=0, sticky='w', pady=5)
        self.array_size_display = ttk.Label(frame, text="200×200 px grid", 
                                            foreground='blue', font=('TkDefaultFont', 10, 'bold'))
        self.array_size_display.grid(row=8, column=1, sticky='w', pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Bind event to update size display
        self.array_size.bind('<KeyRelease>', self.update_array_size_display)
        self.array_rows.bind('<KeyRelease>', self.update_array_size_display)
        self.array_cols.bind('<KeyRelease>', self.update_array_size_display)
        self.array_spacing.bind('<KeyRelease>', self.update_array_size_display)
        
        # Buttons
        btn_frame = ttk.Frame(self.array_tab)
        btn_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(btn_frame, text="Preview", command=self.preview_array).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Generate & Save", command=self.generate_array).pack(side='left', padx=5)
        
        # Info
        info = ttk.Label(self.array_tab, text="Generate a grid of AprilTags.\nPerfect for calibration boards. Export as PNG, SVG, or PDF.", 
                        justify='left', wraplength=600)
        info.pack(padx=10, pady=10)
    
    def browse_dir(self):
        """Browse for output directory"""
        d = filedialog.askdirectory(initialdir=self.batch_dir.get())
        if d:
            self.batch_dir.set(d)
    
    def update_array_size_display(self, event=None):
        """Update array size display"""
        try:
            size_px = int(self.array_size.get())
            full_size_px = int(round(size_without_border_to_full(size_px)))
            size_cm = pixels_to_physical(size_px, dpi=72)
            full_size_cm = pixels_to_physical(full_size_px, dpi=72)
            rows = int(self.array_rows.get())
            cols = int(self.array_cols.get())
            spacing = int(self.array_spacing.get())
            total_w = cols * (full_size_px + spacing) - spacing
            total_h = rows * (full_size_px + spacing) - spacing
            total_w_cm = pixels_to_physical(total_w, dpi=72)
            total_h_cm = pixels_to_physical(total_h, dpi=72)
            self.array_size_display.config(
                text=f"{size_px}px/tag ({size_cm:.1f}cm, no border) → {full_size_px}px ({full_size_cm:.1f}cm full) | Grid: {total_w_cm:.1f}cm × {total_h_cm:.1f}cm ({rows}×{cols})"
            )
        except (ValueError, IndexError):
            pass
    
    def preview_single(self):
        try:
            tag_id = int(self.single_id.get())
            style = self.single_style.get()
            format_type = self.single_format.get()
            
            # Calculate size
            if self.single_size_mode.get() == 'Physical (cm) + DPI':
                size_cm = float(self.single_size_cm.get())
                dpi_str = self.single_dpi.get().split()[0]
                dpi = int(dpi_str)
                size_pixels = calculate_pixels_from_physical(size_cm, dpi)
            else:
                size_pixels = int(self.single_size_pixels.get())

            full_size_pixels = int(round(size_without_border_to_full(size_pixels)))
            
            if format_type == 'PNG (Raster)':
                img = AprilTagGenerator.generate_tag(tag_id, full_size_pixels, style)
                img.show()
            elif format_type == 'SVG (Vector)':
                requested_size_cm = size_cm if self.single_size_mode.get() == 'Physical (cm) + DPI' else pixels_to_physical(size_pixels, dpi=72)
                full_size_cm = size_without_border_to_full(requested_size_cm)
                svg_content = generate_svg_tag(tag_id, full_size_cm, 
                                              int(self.single_dpi.get().split()[0]) if self.single_size_mode.get() == 'Physical (cm) + DPI' else 72,
                                              style)
                messagebox.showinfo("SVG Preview", "SVG format cannot be displayed. Generate and save to file to preview in an SVG viewer.")
            else:  # PDF
                messagebox.showinfo("PDF Preview", "PDF format cannot be previewed in-app. Generate and save to file to view in a PDF viewer.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def generate_single(self):
        try:
            tag_id = int(self.single_id.get())
            style = self.single_style.get()
            format_type = self.single_format.get()
            
            # Calculate size
            if self.single_size_mode.get() == 'Physical (cm) + DPI':
                size_cm = float(self.single_size_cm.get())
                dpi_str = self.single_dpi.get().split()[0]
                dpi = int(dpi_str)
                requested_size_pixels = calculate_pixels_from_physical(size_cm, dpi)
            else:
                size_cm = None
                requested_size_pixels = int(self.single_size_pixels.get())
                dpi = 72

            size_pixels = int(round(size_without_border_to_full(requested_size_pixels)))
            
            if format_type == 'PNG (Raster)':
                f = filedialog.asksaveasfilename(defaultextension=".png", 
                                               initialfile=f"apriltag_{tag_id}.png",
                                               filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
                if f:
                    img = AprilTagGenerator.generate_tag(tag_id, size_pixels, style)
                    img.save(f)
                    # Calculate display size
                    if size_cm is None:
                        size_cm = pixels_to_physical(requested_size_pixels, 72)
                    inches = size_cm / 2.54
                    messagebox.showinfo("Success", f"Saved to:\n{f}\n\nTag Size: {size_cm:.2f}cm × {size_cm:.2f}cm\n({inches:.2f}\" × {inches:.2f}\")  @ {dpi} DPI\n\nPrint to scale for correct dimensions.")
            elif format_type == 'SVG (Vector)':
                f = filedialog.asksaveasfilename(defaultextension=".svg",
                                               initialfile=f"apriltag_{tag_id}.svg",
                                               filetypes=[("SVG files", "*.svg"), ("All files", "*.*")])
                if f:
                    if size_cm is None:
                        size_cm = pixels_to_physical(requested_size_pixels, 72)
                    full_size_cm = size_without_border_to_full(size_cm)
                    svg_content = generate_svg_tag(tag_id, full_size_cm, dpi, style)
                    # Add DPI info to SVG as comment
                    svg_with_info = f"<!-- Generated at {dpi} DPI - Print to scale for {size_cm:.2f}cm × {size_cm:.2f}cm tag -->\n" + svg_content
                    with open(f, 'w') as svg_file:
                        svg_file.write(svg_with_info)
                    inches = size_cm / 2.54
                    messagebox.showinfo("Success", f"Saved to:\n{f}\n\nTag Size: {size_cm:.2f}cm × {size_cm:.2f}cm\n({inches:.2f}\" × {inches:.2f}\") @ {dpi} DPI\n\nPrint to scale for correct dimensions.")
            else:  # PDF
                f = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               initialfile=f"apriltag_{tag_id}.pdf",
                                               filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
                if f:
                    if size_cm is None:
                        size_cm = pixels_to_physical(requested_size_pixels, dpi)
                    full_size_cm = size_without_border_to_full(size_cm)
                    generate_pdf_tag(f, tag_id, size_cm=full_size_cm, style=style)
                    inches = size_cm / 2.54
                    messagebox.showinfo("Success", f"Saved to:\n{f}\n\nTag Size: {size_cm:.2f}cm × {size_cm:.2f}cm\n({inches:.2f}\" × {inches:.2f}\")\n\nVector PDF generated. Print to scale for correct dimensions.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def generate_batch(self):
        try:
            start = int(self.batch_start.get())
            end = int(self.batch_end.get())
            style = self.batch_style.get()
            format_type = self.batch_format.get()
            out_dir = self.batch_dir.get()
            
            # Get size based on mode
            mode = self.batch_size_mode.get()
            if mode == 'Physical (cm) + DPI':
                size_cm = float(self.batch_size_cm.get())
                dpi_str = self.batch_dpi.get().split()[0]
                dpi = int(dpi_str)
                requested_size = calculate_pixels_from_physical(size_cm, dpi)
            else:
                requested_size = int(self.batch_size_pixels.get())
                dpi = 300  # Default DPI for pixel mode
                size_cm = pixels_to_physical(requested_size, dpi)

            size = int(round(size_without_border_to_full(requested_size)))
            
            if start > end:
                messagebox.showerror("Error", "Start ID > End ID")
                return
            if not os.path.exists(out_dir):
                messagebox.showerror("Error", "Output directory not found")
                return
            
            total = end - start + 1
            self.batch_progress['maximum'] = total
            self.batch_progress['value'] = 0
            
            ext = '.svg' if 'SVG' in format_type else ('.pdf' if 'PDF' in format_type else '.png')
            
            for i, tag_id in enumerate(range(start, end + 1)):
                self.batch_status.config(text=f"Generating {i+1}/{total}")
                self.root.update()
                
                if format_type == 'PNG (Raster)':
                    img = AprilTagGenerator.generate_tag(tag_id, size, style)
                    img.save(os.path.join(out_dir, f"apriltag_{tag_id}.png"), dpi=(dpi, dpi))
                elif format_type == 'SVG (Vector)':
                    full_size_cm = size_without_border_to_full(size_cm)
                    svg_content = generate_svg_tag(tag_id, full_size_cm, dpi, style)
                    # Add DPI info to SVG
                    svg_with_info = f"<!-- {size_cm:.2f}cm @ {dpi} DPI -->\n" + svg_content
                    with open(os.path.join(out_dir, f"apriltag_{tag_id}.svg"), 'w') as f:
                        f.write(svg_with_info)
                else:  # PDF
                    full_size_cm = size_without_border_to_full(size_cm)
                    generate_pdf_tag(
                        os.path.join(out_dir, f"apriltag_{tag_id}.pdf"),
                        tag_id,
                        size_cm=full_size_cm,
                        style=style
                    )
                
                self.batch_progress['value'] = i + 1
            
            self.batch_status.config(text=f"Complete: {total} tags")
            inches = size_cm / 2.54
            messagebox.showinfo("Success", f"Generated {total} tags ({format_type})\n\nTag Size: {size_cm:.2f}cm × {size_cm:.2f}cm ({inches:.2f}\" × {inches:.2f}\") each @ {dpi} DPI\n\nFiles are ready to print to scale.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def preview_array(self):
        try:
            start = int(self.array_start.get())
            rows = int(self.array_rows.get())
            cols = int(self.array_cols.get())
            size = int(self.array_size.get())
            full_size = int(round(size_without_border_to_full(size)))
            spacing = int(self.array_spacing.get())
            style = self.array_style.get()
            labels = self.array_labels.get()
            
            img = AprilTagGenerator.generate_tag_array(start, rows, cols, full_size, 
                                                      spacing, style, labels)
            img.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def generate_array(self):
        try:
            start = int(self.array_start.get())
            rows = int(self.array_rows.get())
            cols = int(self.array_cols.get())
            size = int(self.array_size.get())
            full_size = int(round(size_without_border_to_full(size)))
            spacing = int(self.array_spacing.get())
            style = self.array_style.get()
            labels = self.array_labels.get()
            format_type = self.array_format.get()
            
            default_ext = ".pdf" if 'PDF' in format_type else (".svg" if 'SVG' in format_type else ".png")
            initial_name = f"apriltag_array_{rows}x{cols}.pdf" if 'PDF' in format_type else (f"apriltag_array_{rows}x{cols}.svg" if 'SVG' in format_type else f"apriltag_array_{rows}x{cols}.png")
            f = filedialog.asksaveasfilename(defaultextension=default_ext,
                                           initialfile=initial_name,
                                           filetypes=[("PNG files", "*.png"), ("SVG files", "*.svg"), ("PDF files", "*.pdf"), ("All files", "*.*")])
            if f:
                if format_type == 'PNG (Raster)':
                    img = AprilTagGenerator.generate_tag_array(start, rows, cols, full_size,
                                                              spacing, style, labels)
                    img.save(f)
                elif format_type == 'SVG (Vector)':  # SVG - Note: Array SVG export is created by combining individual SVGs
                    # For SVG arrays, we create a composite SVG with all tags
                    tag_ids = list(range(start, start + rows * cols))
                    
                    # Calculate dimensions
                    total_width = cols * (full_size + spacing) - spacing
                    total_height = rows * (full_size + spacing) - spacing
                    
                    svg_lines = [
                        f'<svg width="{total_width}px" height="{total_height}px" viewBox="0 0 {total_width} {total_height}" xmlns="http://www.w3.org/2000/svg">',
                        f'  <rect width="{total_width}" height="{total_height}" fill="white"/>'
                    ]
                    
                    # Add each tag
                    idx = 0
                    for row in range(rows):
                        for col in range(cols):
                            if idx < len(tag_ids) and tag_ids[idx] <= 586:
                                x = col * (full_size + spacing)
                                y = row * (full_size + spacing)
                                
                                # Get pattern for this tag
                                from tag36h11_complete import Tag36h11
                                pattern = Tag36h11.generate_tag_pattern(tag_ids[idx])
                                
                                # Add tag as group
                                svg_lines.append(f'  <g transform="translate({x}, {y})">')
                                svg_lines.append(f'    <rect width="{full_size}" height="{full_size}" fill="white"/>')
                                
                                # Add pixels
                                pattern_size = pattern.shape[0]
                                cell_size = full_size / pattern_size
                                
                                for i in range(pattern_size):
                                    for j in range(pattern_size):
                                        if pattern[i, j] == 1:
                                            px = int(j * cell_size)
                                            py = int(i * cell_size)
                                            pw = int(cell_size)
                                            ph = int(cell_size)
                                            svg_lines.append(f'    <rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="black"/>')
                                
                                svg_lines.append(f'  </g>')
                            idx += 1
                    
                    svg_lines.append('</svg>')
                    
                    with open(f, 'w') as svg_file:
                        svg_file.write('\n'.join(svg_lines))
                else:  # PDF
                    generate_pdf_array(
                        f,
                        start_id=start,
                        rows=rows,
                        cols=cols,
                        tag_size_px=full_size,
                        spacing_px=spacing,
                        style=style,
                        add_labels=labels,
                        dpi=72
                    )
                
                messagebox.showinfo("Success", f"Saved to:\n{f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = AprilTagGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
