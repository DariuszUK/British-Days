#!/usr/bin/env python3
"""
Database manager for British Days application.
Handles SQLite database operations for storing British slang/phrases.
"""
import sqlite3
import os
import sys
import json
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Manages the SQLite database for British slang terms."""
    
    def __init__(self, config_path='config.json', config=None):
        """Initialize database manager.
        
        Args:
            config_path: Path to config file (default: 'config.json')
            config: Pre-loaded config dict to use instead of loading from file
        """
        self.config = config if config is not None else self._load_config(config_path)
        self.data_dir = self._get_data_directory()
        self.db_path = os.path.join(self.data_dir, self.config.get('database_name', 'british_slang.db'))
        self._initialize_database()
    
    def _load_config(self, config_path):
        """Load configuration from JSON file with proper error handling and defaults.
        
        Args:
            config_path: Path to the JSON config file
            
        Returns:
            dict: Configuration with all required keys
        """
        # Define default configuration
        default_config = {
            'data_directory': 'Data',
            'database_name': 'british_slang.db',
            'window_title': 'British Days - Slang Collector',
            'window_width': 800,
            'window_height': 600
        }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                
            # Merge loaded config with defaults (loaded config takes precedence)
            config = default_config.copy()
            config.update(loaded_config)
            return config
            
        except FileNotFoundError:
            # Config file doesn't exist, use defaults
            print(f"Warning: Config file '{config_path}' not found. Using default configuration.")
            return default_config
        except json.JSONDecodeError as e:
            # Config file is malformed
            print(f"Warning: Config file '{config_path}' is malformed: {e}. Using default configuration.")
            return default_config
        except Exception as e:
            # Any other error
            print(f"Warning: Error loading config from '{config_path}': {e}. Using default configuration.")
            return default_config
    
    def _get_data_directory(self):
        """Get the Data directory path relative to the executable.
        
        Creates the directory if it doesn't exist.
        
        Returns:
            str: Path to the data directory
        """
        # Get the directory where the script/exe is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Use .get() with default to safely access data_directory
        data_dir_name = self.config.get('data_directory', 'Data')
        data_dir = os.path.join(base_path, data_dir_name)
        
        # Create directory if it doesn't exist
        try:
            os.makedirs(data_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create data directory '{data_dir}': {e}")
            print(f"Using current directory instead.")
            data_dir = base_path
        
        return data_dir
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create slang terms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slang_terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL UNIQUE,
                definition TEXT,
                example TEXT,
                category TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT
            )
        ''')
        
        # Create search history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result_count INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_term(self, term, definition='', example='', category='slang', source='internet'):
        """Add a new slang term to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO slang_terms (term, definition, example, category, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (term, definition, example, category, source))
            
            conn.commit()
            term_id = cursor.lastrowid
            conn.close()
            
            return True, term_id
        except sqlite3.IntegrityError:
            # Term already exists
            return False, None
        except Exception as e:
            print(f"Error adding term: {e}")
            return False, None
    
    def get_all_terms(self):
        """Retrieve all slang terms from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, term, definition, example, category, date_added, source
            FROM slang_terms
            ORDER BY date_added DESC
        ''')
        
        terms = cursor.fetchall()
        conn.close()
        
        return terms
    
    def get_term_by_id(self, term_id):
        """Get a specific term by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, term, definition, example, category, date_added, source
            FROM slang_terms
            WHERE id = ?
        ''', (term_id,))
        
        term = cursor.fetchone()
        conn.close()
        
        return term
    
    def search_terms(self, search_query):
        """Search for terms matching the query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, term, definition, example, category, date_added, source
            FROM slang_terms
            WHERE term LIKE ? OR definition LIKE ?
            ORDER BY date_added DESC
        ''', (f'%{search_query}%', f'%{search_query}%'))
        
        terms = cursor.fetchall()
        conn.close()
        
        return terms
    
    def add_search_history(self, search_term, result_count):
        """Record a search in the history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (search_term, result_count)
            VALUES (?, ?)
        ''', (search_term, result_count))
        
        conn.commit()
        conn.close()
    
    def get_database_stats(self):
        """Get statistics about the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM slang_terms')
        total_terms = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM search_history')
        total_searches = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_terms': total_terms,
            'total_searches': total_searches,
            'database_path': self.db_path
        }


# For standalone testing
if __name__ == '__main__':
    import sys
    
    db = DatabaseManager()
    print("Database initialized successfully!")
    print(f"Database location: {db.db_path}")
    
    # Add some test data
    test_terms = [
        ('mate', 'Friend or buddy', 'Alright, mate?', 'greeting'),
        ('chuffed', 'Very pleased', 'I\'m chuffed to bits!', 'emotion'),
        ('knackered', 'Extremely tired', 'I\'m absolutely knackered.', 'state'),
    ]
    
    for term, definition, example, category in test_terms:
        success, tid = db.add_term(term, definition, example, category, 'test')
        if success:
            print(f"Added: {term} (ID: {tid})")
        else:
            print(f"Already exists: {term}")
    
    # Display stats
    stats = db.get_database_stats()
    print(f"\nDatabase Stats:")
    print(f"Total terms: {stats['total_terms']}")
    print(f"Total searches: {stats['total_searches']}")
