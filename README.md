# British Days - Slang Collector

A single-window Windows application that automatically searches for British slang terms from multiple sources (Wikipedia, Wiktionary, and internal database) and stores them in a local database. The GUI is built entirely from PNG elements for a custom, polished look.

## Features

- **Automatic Search**: Searches for new British slang terms from multiple sources with intelligent caching
- **Real API Integration**: Fetches data from Wikipedia and Wiktionary APIs
- **Smart Caching**: Avoids re-searching already visited sources and caches found terms
- **No Record Limit**: Removed the 33-record limitation - search continues until stopped
- **Database Storage**: All terms stored in SQLite database in the `Data` directory
- **PNG-Based GUI**: Entire interface built using custom PNG graphics
- **Resizable Columns**: Drag-and-drop column resizing with automatic width persistence
- **Easy Configuration**: Simple JSON configuration file for customization
- **Portable**: Database and data stored relative to the executable

## New in This Version

### API Integration
- **Wikipedia API**: Searches British slang categories on Wikipedia
- **Wiktionary API**: Searches British English terms on Wiktionary
- **Fallback System**: Automatically falls back to mock database if APIs fail
- **Source Rotation**: Intelligently rotates between sources for variety

### Search Optimization
- **Location Tracking**: Remembers which Wikipedia/Wiktionary pages have been searched
- **Term Caching**: Caches API results to avoid duplicate API calls
- **Smart Duplicate Detection**: Skips terms already in the database

### UI Improvements
- **Resizable Columns**: Click and drag column borders to resize
- **Persistent Column Widths**: Column widths are saved to `config.json` automatically
- **No Search Limit**: Removed the 33/50 record limit - search continues indefinitely

## Installation

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
├── main.py              # Main application entry point with column resizing
├── database.py          # Enhanced database with caching and tracking
├── search.py            # Search with Wikipedia/Wiktionary API integration
├── generate_assets.py   # PNG asset generator
├── build.py            # Build script for creating .exe
├── config.json         # Configuration file (includes column widths)
├── requirements.txt    # Python dependencies
├── test_app.py         # Basic test suite
├── test_enhanced_features.py  # Enhanced features test suite
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
    "data_directory": "Data",
    "database_name": "british_slang.db",
    "window_title": "British Days - Slang Collector",
    "window_width": 800,
    "window_height": 600,
    "column_widths": {
        "#0": 50,
        "term": 120,
        "definition": 250,
        "example": 200,
        "category": 100,
        "polish": 150,
        "pronunciation": 120
    },
    "search_api": {
        "type": "api",                    // "api" or "mock"
        "sources": ["wikipedia", "wiktionary", "mock"],
        "wikipedia_endpoint": "https://en.wikipedia.org/w/api.php",
        "wiktionary_endpoint": "https://en.wiktionary.org/w/api.php",
        "max_retries": 3,
        "timeout": 10,
        "fallback_terms": [...]           // Fallback slang terms
    }
}
```

### Configuration Options

- **type**: Set to `"api"` to use real APIs, or `"mock"` to use only the internal database
- **sources**: Array of sources to use (order determines rotation)
- **column_widths**: Automatically updated when you resize columns in the GUI
- **timeout**: API request timeout in seconds

## How It Works

1. **On Launch**: The application loads previous column settings and initializes database
2. **Search**: Click "Search" to automatically find new terms from Wikipedia, Wiktionary, or internal database
3. **Smart Caching**: The app remembers which sources it has searched and caches results
4. **Display**: All terms displayed in the main panel with resizable columns
5. **Column Resize**: Drag column borders to resize - widths are saved automatically
6. **Database**: All data stored in `Data/british_slang.db` next to the executable

## Database Schema

**slang_terms table:**
- `id`: Primary key
- `term`: The slang word/phrase (unique, case-insensitive)
- `definition`: Meaning of the term
- `example`: Usage example
- `category`: Category (e.g., greeting, emotion, action)
- `date_added`: When the term was added
- `source`: Where the term was found
- `polish`: Polish translation
- `pronunciation`: Pronunciation guide

**search_history table:**
- `id`: Primary key
- `search_term`: What was searched
- `search_date`: When the search occurred
- `result_count`: Number of results found

**searched_locations table:** *(NEW)*
- `id`: Primary key
- `source_type`: Source type (wikipedia, wiktionary, etc.)
- `source_identifier`: Unique identifier for the location
- `search_date`: When it was searched
- `terms_found`: Number of terms found

**term_cache table:** *(NEW)*
- `id`: Primary key
- `term`: Cached term (unique, case-insensitive)
- `definition`, `example`, `category`, `polish`, `pronunciation`: Term details
- `source_type`: Where it came from
- `source_url`: Original URL
- `cache_date`: When it was cached
- `added_to_database`: Whether it's been added to main database

## API Integration Details

### Wikipedia API
- Searches articles in "Category:British slang"
- Extracts definitions and examples from article content
- Tracks which articles have been searched to avoid duplicates
- Falls back to Wiktionary or mock if no results

### Wiktionary API
- Searches for British English terms
- Rotates through different starting letters for variety
- Parses page content to extract definitions
- Tracks searched terms to avoid duplicates

### Fallback System
- If APIs fail (network issues, rate limits, etc.), automatically falls back to mock database
- Mock database contains 35 well-documented British slang terms
- Graceful degradation ensures the app always works

## Testing

Run the comprehensive test suite:

```bash
# Basic tests
python test_app.py

# Enhanced features tests
python test_enhanced_features.py
```

## Customization

### Changing PNG Assets

1. Edit `generate_assets.py` to customize colors, sizes, and text
2. Run `python generate_assets.py` to regenerate assets
3. Restart the application to see changes

### Adding More Mock Slang Terms

Edit the `slang_database` list in `search.py` to add more British slang terms to the fallback database.

### Changing Column Widths

Simply drag the column borders in the running application. Your changes are saved automatically to `config.json`.

## Requirements

- Python 3.8+
- Pillow (for PNG handling)
- tkinter (usually included with Python)
- requests (for API integration)

## Troubleshooting

### API Not Working
If you see "Wikipedia search error" or "Wiktionary search error" in the logs:
- Check your internet connection
- The app will automatically fall back to the mock database
- Set `"type": "mock"` in config.json to disable API searches

### Column Widths Not Saving
- Ensure config.json is writable
- Check file permissions in the application directory
- Manually edit column_widths in config.json if needed

### Search Stops After Some Terms
- The search will stop after 10 consecutive failures (duplicates or errors)
- Click "Stop" and then "Search" again to continue
- This prevents infinite loops when all available sources are exhausted

## License

This project is open source and available for educational purposes.

## Author

Created for British slang enthusiasts and language learners!