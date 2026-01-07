#!/usr/bin/env python3
"""
Build script to create a Windows executable using PyInstaller.
"""
import os
import sys
import subprocess
import shutil


def build_executable():
    """Build the Windows executable."""
    print("Building British Days executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable file
        '--windowed',  # No console window
        '--name=BritishDays',
        '--add-data=assets:assets',  # Include assets folder
        '--add-data=config.json:.',  # Include config file
        '--icon=assets/logo.png' if os.path.exists('assets/logo.png') else '',
        'main.py'
    ]
    
    # Remove empty icon parameter if logo doesn't exist
    cmd = [c for c in cmd if c]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ Build successful!")
        print("\nExecutable location:")
        print("  - Windows: dist/BritishDays.exe")
        print("\nNote: The 'Data' directory will be created automatically")
        print("next to the executable when you run it for the first time.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False
    
    return True


if __name__ == '__main__':
    build_executable()
