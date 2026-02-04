#!/bin/bash
# AprilTag Generator Launcher (Linux/Mac)
# This script launches the AprilTag Generator application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Run the application using the virtual environment
.venv/bin/python apriltag_generator.py
