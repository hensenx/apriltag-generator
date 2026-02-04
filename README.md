# AprilTag Generator

A professional Python GUI application for generating AprilTag fiducial markers. AprilTags are used in computer vision for camera pose estimation, augmented reality, and robotics applications.

## Features

### Core Functionality
- **Single Tag Generation**: Create individual AprilTags with custom IDs (0-586)
- **Batch Generation**: Generate multiple individual tag files at once
- **Array Generation**: Create checkerboard-style arrays of multiple tags
- **All 587 Official Tags**: Complete tag36h11 library from AprilRobotics
- **Multiple Rendering Styles**: Rectangular and circular tag options

### New in v2.0: DPI & SVG Support
- **DPI-Based Sizing**: Specify physical dimensions (cm) + DPI for professional printing
- **SVG Export**: Generate scalable vector graphics (infinitely scalable, 80% smaller than PNG)
- **Format Selection**: Choose between PNG (raster) or SVG (vector) formats
- **DPI Presets**: 72, 96, 150, 300, 600 DPI for different use cases
- **Smart UI**: Dynamic size mode selector (pixels or physical + DPI)

### Customizable Settings
- **Tag Size**: Pixels or physical dimensions (centimeters) + DPI
- **Rendering Style**: Rectangular or circular
- **Export Format**: PNG (raster) or SVG (vector)
- **Array Dimensions**: Rows × columns for calibration boards
- **Spacing & Labels**: Adjustable spacing and optional ID labels
- **Output Directory**: Choose where to save files

## Installation

### Requirements
- Python 3.8+
- pip (Python package manager)

### Setup

1. Clone or download this repository

2. Install required packages:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install numpy pillow
```

## Quick Start

### GUI Usage

**Windows:**
```bash
run_apriltag_generator.bat
```

**Linux/Mac:**
```bash
chmod +x run_apriltag_generator.sh
./run_apriltag_generator.sh
```

**Manual (any OS):**
```bash
python apriltag_generator.py
```

### Command-Line Usage

Generate a professional-quality SVG tag:
```python
from apriltag_generator import generate_svg_tag

# 10cm at 300 DPI (print quality)
svg = generate_svg_tag(0, size_cm=10, dpi=300, style='rectangular')
with open('apriltag.svg', 'w') as f:
    f.write(svg)
```

## Documentation

### For Quick Start
→ **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick commands and workflows

### For Detailed Usage
→ **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage guide with examples

### For Feature Details
→ **[DPI_SVG_FEATURES.md](DPI_SVG_FEATURES.md)** - Complete feature documentation

### For Technical Details
→ **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## Supported Formats

| Format | Type | Best For | File Size |
|--------|------|----------|-----------|
| PNG | Raster | Web, quick preview | Large |
| SVG | Vector | Professional print, scaling | Small (3-4 KB) |

## DPI Reference

| DPI | Purpose | Example Use |
|-----|---------|------------|
| 72 | Screen display | On-screen preview |
| 96 | Web | Web images |
| 150 | Photo prints | Photo quality |
| 300 | Professional print | Recommended for printing |
| 600 | High resolution | Highest quality prints |

## Size Examples (10cm at 300 DPI)

- Physical: 10 cm × 10 cm
- Resolution: 1181 × 1181 pixels
- SVG: 3.7 KB
- PNG: 89 KB

## GUI Tabs

### Single Tag Tab
- Generate individual tags with flexible sizing
- Choose between pixel or physical (cm + DPI) sizing
- Export as PNG or SVG

### Batch Tab
- Generate multiple tags (tag range)
- Create individual files or array
- SVG batch creates separate .svg files

### Array Tab
- Create grid layouts for calibration
- Multiple tags in single file
- Adjustable spacing and labels
- Export as PNG composite or SVG composite

## Example Workflows

### Print Professional 10cm Tags
1. Single Tag Tab → Size Mode: Physical (cm) + DPI
2. Set Size: 10 cm, DPI: 300 (Print)
3. Export Format: SVG (Vector)
4. Generate & Save

### Quick Web Batch
1. Batch Tab → Start: 0, End: 99
2. Size: 300 pixels
3. Export Format: PNG (Raster)
4. Generate All

### Create Calibration Board
1. Array Tab → Rows: 5, Cols: 5
2. Tag Size: 150 pixels
3. Export Format: PNG
4. Generate & Save

## Testing

Run comprehensive feature tests:

```bash
python test_dpi_svg.py
```

All 4 test categories with 20+ validations should pass.

## Performance

- SVG Generation: ~1-2ms per tag
- PNG Generation: ~5-10ms per tag
- Batch 100 tags: ~150-200ms (SVG) or ~500-1000ms (PNG)

### Batch Generate Tab
1. Enter the starting and ending Tag IDs
2. Set the tag size and border width
3. Choose the output directory
4. Click "Generate All Tags" to create all files at once
5. Progress bar shows generation status

### Tag Array Tab
1. Enter the starting Tag ID
2. Set the number of rows and columns
3. Configure tag size and spacing
4. Choose whether to include ID labels
5. Click "Preview" to view the array
6. Click "Generate & Save" to export as PNG

## Use Cases

- **Camera Calibration**: Print tag arrays for calibration boards
- **Pose Estimation**: Track camera position relative to tags
- **Augmented Reality**: Use as anchors for AR content
- **Robotics**: Navigate and localize robots
- **Motion Capture**: Track objects in 3D space

## Tips

- Use a border width of at least 1 for reliable detection
- Print tags on white paper with good contrast
- Ensure tags are flat and well-lit for detection
- Larger tags are easier to detect from farther distances
- Sequential tag IDs in arrays make tracking easier

## File Output

- Single tags: `apriltag_{ID}.png`
- Batch tags: `apriltag_0.png`, `apriltag_1.png`, etc. (one file per tag)
- Arrays: `apriltag_array_{rows}x{cols}.png`

All files are saved as high-quality PNG images suitable for printing.
