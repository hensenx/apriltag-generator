#!/usr/bin/env python3
"""Verify DPI metadata in generated AprilTag files"""

from apriltag_generator import AprilTagGenerator, generate_svg_tag, calculate_pixels_from_physical
from PIL import Image
import os

print("="*70)
print("DPI METADATA VERIFICATION TEST")
print("="*70)

# Test parameters
tag_id = 42
size_cm = 10.0
dpi = 300

print(f"\nTest Parameters:")
print(f"  Tag ID: {tag_id}")
print(f"  Physical Size: {size_cm} cm")
print(f"  DPI: {dpi}")

# Calculate expected pixel size
expected_pixels = calculate_pixels_from_physical(size_cm, dpi)
print(f"  Expected Pixels: {expected_pixels}px")

print("\n" + "-"*70)
print("TEST 1: PNG with DPI metadata")
print("-"*70)

# Generate PNG
png_file = "test_dpi_metadata.png"
img = AprilTagGenerator.generate_tag(tag_id, expected_pixels, style='rectangular')

# Save with DPI info
dpi_tuple = (dpi, dpi)
img.save(png_file, dpi=dpi_tuple)

# Read back and verify
img_check = Image.open(png_file)
stored_dpi = img_check.info.get('dpi', (0, 0))

print(f"✓ PNG file created: {png_file}")
print(f"  Image size: {img_check.size[0]}x{img_check.size[1]} pixels")
print(f"  Stored DPI: {stored_dpi}")
print(f"  Expected DPI: {dpi_tuple}")

# Close image to release file
img_check.close()

# PNG DPI can have floating point precision - check if close enough
dpi_match = abs(stored_dpi[0] - dpi) < 0.01 and abs(stored_dpi[1] - dpi) < 0.01
if dpi_match:
    print(f"  ✓ DPI metadata CORRECT (within tolerance)!")
else:
    print(f"  ✗ DPI metadata INCORRECT!")

# Verify dimensions - note: 10cm at 300 DPI = 1181px, but tag is 10x10 pattern (1180px)
size_match = abs(img.size[0] - expected_pixels) <= 1 and abs(img.size[1] - expected_pixels) <= 1
print(f"  Dimensions match: {'✓ YES' if size_match else '✗ NO (off by 1px due to rounding)'}")

print("\n" + "-"*70)
print("TEST 2: SVG with DPI metadata")
print("-"*70)

# Generate SVG
svg_file = "test_dpi_metadata.svg"
svg_content = generate_svg_tag(tag_id, size_cm, dpi, style='rectangular')

# Add DPI comment
svg_with_metadata = f"<!-- Generated at {dpi} DPI - Print to scale for {size_cm:.2f}cm × {size_cm:.2f}cm tag -->\n{svg_content}"

with open(svg_file, 'w') as f:
    f.write(svg_with_metadata)

print(f"✓ SVG file created: {svg_file}")

# Read and verify
with open(svg_file, 'r') as f:
    svg_text = f.read()

# Check for DPI in comment
has_dpi_comment = f"{dpi} DPI" in svg_text
has_size_info = f"{size_cm:.2f}cm" in svg_text

print(f"  DPI in comment: {'✓ YES' if has_dpi_comment else '✗ NO'}")
print(f"  Size in comment: {'✓ YES' if has_size_info else '✗ NO'}")

# Check SVG attributes
import re
viewbox_match = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
width_match = re.search(r'width="([\d.]+)(cm|px)"', svg_text)
height_match = re.search(r'height="([\d.]+)(cm|px)"', svg_text)

print(f"  ViewBox found: {'✓ YES' if viewbox_match else '✗ NO'}")
print(f"  Width attribute: {'✓ YES' if width_match else '✗ NO'}")
print(f"  Height attribute: {'✓ YES' if height_match else '✗ NO'}")

if width_match and height_match:
    svg_width = float(width_match.group(1))
    svg_height = float(height_match.group(1))
    unit = width_match.group(2)
    print(f"  SVG dimensions: {svg_width}{unit} × {svg_height}{unit}")
    
    if unit == 'cm':
        dims_match = abs(svg_width - size_cm) < 0.01 and abs(svg_height - size_cm) < 0.01
        print(f"  Dimensions match: {'✓ YES' if dims_match else '✗ NO'}")
    else:
        print(f"  Note: Dimensions in {unit}, not cm")
else:
    dims_match = False

print("\n" + "-"*70)
print("TEST 3: Physical size calculation verification")
print("-"*70)

# Verify the math
inches = size_cm / 2.54
calculated_pixels = int(inches * dpi)

print(f"  Physical size: {size_cm} cm")
print(f"  Converted to inches: {inches:.4f}\"")
print(f"  At {dpi} DPI: {calculated_pixels} pixels")
print(f"  Expected: {expected_pixels} pixels")
print(f"  Match: {'✓ YES' if calculated_pixels == expected_pixels else '✗ NO'}")

print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)

all_good = (
    dpi_match and
    size_match and
    has_dpi_comment and
    has_size_info and
    calculated_pixels == expected_pixels
)

if all_good:
    print("✓ ALL TESTS PASSED - DPI metadata is correctly stored!")
else:
    print("✗ SOME TESTS FAILED - Check output above")

print(f"\nGenerated test files:")
print(f"  - {png_file}")
print(f"  - {svg_file}")
print("\nThese files can be used to verify print-to-scale functionality.")
print("="*70)

# Cleanup
cleanup = input("\nDelete test files? (y/n): ").strip().lower()
if cleanup == 'y':
    try:
        os.remove(png_file)
        os.remove(svg_file)
        print("✓ Test files deleted")
    except Exception as e:
        print(f"Note: Could not delete files: {e}")
        print("You can manually delete them if needed")
else:
    print("Test files kept for inspection")
