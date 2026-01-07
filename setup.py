#!/usr/bin/env python3
"""
Setup script for British Days application.
Installs dependencies and generates assets.
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(e.stderr)
        return False


def main():
    """Main setup routine."""
    print("=" * 60)
    print("British Days Application - Setup")
    print("=" * 60)
    
    # Step 1: Check Python version
    print(f"\nPython version: {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print("✓ Python version OK")
    
    # Step 2: Install dependencies
    if not run_command(
        [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
        "Installing dependencies"
    ):
        return False
    
    # Step 3: Generate PNG assets
    if not run_command(
        [sys.executable, 'generate_assets.py'],
        "Generating PNG assets"
    ):
        return False
    
    # Step 4: Verify assets
    assets_dir = 'assets'
    required_assets = [
        'background.png', 'btn_search.png', 'btn_refresh.png',
        'btn_exit.png', 'panel_main.png', 'logo.png'
    ]
    
    print("\nVerifying assets...")
    all_exist = True
    for asset in required_assets:
        path = os.path.join(assets_dir, asset)
        if os.path.exists(path):
            print(f"  ✓ {asset}")
        else:
            print(f"  ✗ {asset} missing")
            all_exist = False
    
    if not all_exist:
        print("✗ Some assets are missing")
        return False
    
    # Step 5: Create Data directory
    os.makedirs('Data', exist_ok=True)
    print("\n✓ Data directory created")
    
    # Success
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nYou can now run the application:")
    print("  python main.py")
    print("\nOr run tests:")
    print("  python test_app.py")
    print("\nTo build a Windows executable:")
    print("  python build.py")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
