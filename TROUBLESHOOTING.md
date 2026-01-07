# Troubleshooting Guide for British Days

## Common Issues and Solutions

### Issue: "Assets directory not found" or "Required PNG asset not found"

**Solution:**
Run the asset generator:
```bash
python generate_assets.py
```

This will create all the required PNG files in the `assets` folder.

### Issue: "ModuleNotFoundError: No module named 'PIL'"

**Solution:**
Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install Pillow directly:
```bash
pip install Pillow
```

### Issue: "ModuleNotFoundError: No module named 'tkinter'"

**Solution:**
Tkinter usually comes with Python, but on some Linux systems you may need to install it:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter
```

**Windows/Mac:**
Tkinter should be included with Python. Try reinstalling Python from python.org.

### Issue: Application starts but shows errors about database

**Solution:**
The application will automatically create the `Data` directory and database file on first run. If you're having issues:

1. Make sure you have write permissions in the application directory
2. Delete the `Data` folder and let the application recreate it
3. Check that you're running the application from the correct directory

### Issue: "Database is locked" error

**Solution:**
1. Close all instances of the application
2. Delete or move the `Data/british_slang.db` file
3. Restart the application (it will create a new database)

### Issue: Application window doesn't appear

**Solution:**
1. Make sure you have a display/desktop environment
2. Check if an error message was printed to the console
3. Try running with error output:
   ```bash
   python main.py 2>&1 | tee error.log
   ```
4. Check `error.log` for details

### Issue: Cannot run on Windows - "Python is not recognized"

**Solution:**
1. Install Python from python.org
2. During installation, check "Add Python to PATH"
3. Restart your command prompt/PowerShell
4. Verify with: `python --version`

### Issue: Assets look wrong or buttons don't work

**Solution:**
1. Delete the `assets` folder
2. Run `python generate_assets.py` again
3. Restart the application

## Getting Help

If you continue to have issues:

1. Check that you're running Python 3.8 or higher: `python --version`
2. Verify all files are present (see README.md for file structure)
3. Run the test suite: `python test_app.py`
4. Check the console output for specific error messages

## System Requirements

- Python 3.8 or higher
- Pillow library
- Tkinter (usually included with Python)
- Windows, macOS, or Linux with desktop environment
- ~50MB of disk space
