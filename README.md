# AprilTag Generator

A Python GUI application for generating AprilTag fiducial markers. AprilTags are used in computer vision for camera pose estimation, augmented reality, and robotics applications.

## Features

- **Single Tag Generation**: Create individual AprilTags with custom IDs
- **Batch Generation**: Generate multiple individual tag files at once
- **Array Generation**: Create checkerboard-style arrays of multiple tags
- **Customizable Settings**:
  - Tag size (pixels)
  - Border width
  - Array dimensions (rows × columns)
  - Spacing between tags
  - Optional ID labels
- **Preview & Export**: Preview tags before saving as PNG files

## Installation

1. Make sure Python 3.8+ is installed
2. Install required packages:
```bash
pip install numpy opencv-python Pillow pupil-apriltags
```

## Usage

### Option 1: Using Launch Scripts (Recommended)

**Windows:**
- Double-click `run_apriltag_generator.bat`

**Linux/Mac:**
```bash
chmod +x run_apriltag_generator.sh
./run_apriltag_generator.sh
```

### Option 2: Manual Launch
```bash
python apriltag_generator.py
```

### Single Tag Tab
1. Enter the desired Tag ID (0-1000)
2. Set the tag size in pixels (recommended: 400)
3. Choose border width (recommended: 1)
4. Click "Preview" to view the tag
5. Click "Generate & Save" to export as PNG

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
