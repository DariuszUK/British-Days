# British Days - Slang Collector

A single-window Windows application that automatically searches for British slang terms and stores them in a local database. The GUI is built entirely from PNG elements for a custom, polished look.

## Features

- **Automatic Search**: Searches for a new British slang term on each launch
- **Database Storage**: All terms are stored in a SQLite database in the `Data` directory
- **PNG-Based GUI**: Entire interface built using custom PNG graphics
- **Easy Configuration**: Simple JSON configuration file for customization
- **Portable**: Database and data stored relative to the executable

## Installation

### Quick Start (Windows)

**The easiest way to run the application on Windows:**

1. Download or clone this repository
2. Double-click `run.bat`

The batch file will automatically:
- Check if Python is installed
- Install required dependencies
- Generate PNG assets if needed
- Create the Data directory
- Run the application

### Running from Source

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate PNG assets:
   ```bash
   python generate_assets.py
   ```
4. Run the application:
   ```bash
   python main.py
   ```

**Alternative:** Run the setup script first:
```bash
python setup.py
python main.py
```

### Building Windows Executable

1. Install dependencies and build tools:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. Generate assets (if not already done):
   ```bash
   python generate_assets.py
   ```
3. Build the executable:
   ```bash
   python build.py
   ```
4. Find the executable in `dist/BritishDays.exe`

## Project Structure

```
British-Days/
├── main.py              # Main application entry point
├── database.py          # Database management module
├── search.py            # Internet search functionality
├── generate_assets.py   # PNG asset generator
├── build.py            # Build script for creating .exe
├── config.json         # Configuration file
├── requirements.txt    # Python dependencies
├── assets/             # PNG graphics (generated)
│   ├── background.png
│   ├── btn_search.png
│   ├── btn_refresh.png
│   ├── btn_exit.png
│   ├── panel_main.png
│   └── logo.png
└── Data/               # Database directory (auto-created)
    └── british_slang.db

```

## Configuration

Edit `config.json` to customize the application:

```json
{
    "data_directory": "Data",           // Database directory name
    "database_name": "british_slang.db", // Database file name
    "window_title": "British Days - Slang Collector",
    "window_width": 800,
    "window_height": 600,
    "search_api": {
        "type": "mock",                 // "mock" or "api"
        "fallback_terms": [...]         // Fallback slang terms
    }
}
```

## How It Works

1. **On Launch**: The application automatically searches for a new British slang term
2. **Search**: Click the "Search" button to manually find a new term
3. **Display**: All terms are displayed in the main panel with definitions and examples
4. **Refresh**: Click "Refresh" to reload the display from the database
5. **Database**: All data is stored in `Data/british_slang.db` next to the executable

## Database Schema

**slang_terms table:**
- `id`: Primary key
- `term`: The slang word/phrase
- `definition`: Meaning of the term
- `example`: Usage example
- `category`: Category (e.g., greeting, emotion, action)
- `date_added`: When the term was added
- `source`: Where the term was found

**search_history table:**
- `id`: Primary key
- `search_term`: What was searched
- `search_date`: When the search occurred
- `result_count`: Number of results found

## Customization

### Changing PNG Assets

1. Edit `generate_assets.py` to customize colors, sizes, and text
2. Run `python generate_assets.py` to regenerate assets
3. Restart the application to see changes

### Adding More Slang Terms

Edit the `slang_database` list in `search.py` to add more British slang terms to the mock database.

### Integrating a Real API

To use a real API for searching:
1. Update `config.json` to set `"type": "api"`
2. Implement the `_api_search()` method in `search.py`
3. Add your API credentials to the configuration

## Requirements

- Python 3.8+
- Pillow (for PNG handling)
- tkinter (usually included with Python)
- requests (for future API integration)

## License

This project is open source and available for educational purposes.

## Author

Created for British slang enthusiasts and language learners!