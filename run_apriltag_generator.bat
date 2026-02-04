@echo off
REM AprilTag Generator Launcher (Windows)
REM This script launches the AprilTag Generator application

cd /d "%~dp0"
".venv\Scripts\python.exe" apriltag_generator.py
pause
