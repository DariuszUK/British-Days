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
import threading


class DatabaseManager:
    """Manages the SQLite database for British slang terms."""
    
    def __init__(self, config_path='config.json'):
        """Initialize database manager."""
        self.config = self._load_config(config_path)
        self.data_dir = self._get_data_directory()
        self.db_path = os.path.join(self.data_dir, self.config.get('database_name', 'british_slang.db'))
        self._lock = threading.Lock()
        self._initialize_database()
    
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'data_directory': 'Data',
                'database_name': 'british_slang.db'
            }
    
    def _get_data_directory(self):
        """Get the Data directory path relative to the executable."""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        data_dir_name = self.config.get('data_directory', 'Data')
        data_dir = os.path.join(base_path, data_dir_name)
        os.makedirs(data_dir, exist_ok=True)
        
        return data_dir
    
    def _get_connection(self):
        """Get a database connection with proper settings."""
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if we need to migrate (add new columns)
            cursor.execute("PRAGMA table_info(slang_terms)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'slang_terms' not in self._get_tables(cursor):
                # Create new table
                cursor.execute('''
                    CREATE TABLE slang_terms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        term TEXT NOT NULL UNIQUE COLLATE NOCASE,
                        definition TEXT,
                        example TEXT,
                        category TEXT,
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source TEXT,
                        polish TEXT,
                        pronunciation TEXT
                    )
                ''')
            else:
                # Add new columns if they don't exist
                if 'polish' not in columns:
                    cursor.execute('ALTER TABLE slang_terms ADD COLUMN polish TEXT')
                if 'pronunciation' not in columns:
                    cursor.execute('ALTER TABLE slang_terms ADD COLUMN pronunciation TEXT')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_term TEXT,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result_count INTEGER
                )
            ''')
            
            # Table to track which sources/locations have been searched
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS searched_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_identifier TEXT NOT NULL,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    terms_found INTEGER DEFAULT 0,
                    UNIQUE(source_type, source_identifier)
                )
            ''')
            
            # Table to cache API search results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS term_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    definition TEXT,
                    example TEXT,
                    category TEXT,
                    polish TEXT,
                    pronunciation TEXT,
                    source_type TEXT,
                    source_url TEXT,
                    cache_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_to_database BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def _get_tables(self, cursor):
        """Get list of existing tables."""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]
    
    def add_term(self, term, definition='', example='', category='slang', source='internet', polish='', pronunciation=''):
        """Add a new slang term to the database."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO slang_terms (term, definition, example, category, source, polish, pronunciation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (term, definition, example, category, source, polish, pronunciation))
                
                conn.commit()
                term_id = cursor.lastrowid
                conn.close()
                
                return True, term_id
            except sqlite3.IntegrityError:
                if conn:
                    conn.close()
                return False, None
            except Exception as e:
                if conn:
                    conn.close()
                print(f"Error adding term: {e}")
                return False, None
    
    def update_term(self, term_id, term, definition='', example='', category='slang', polish='', pronunciation=''):
        """Update an existing term."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE slang_terms 
                    SET term=?, definition=?, example=?, category=?, polish=?, pronunciation=?
                    WHERE id=?
                ''', (term, definition, example, category, polish, pronunciation, term_id))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                if conn:
                    conn.close()
                print(f"Error updating term: {e}")
                return False
    
    def delete_term(self, term_id):
        """Delete a term from the database."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM slang_terms WHERE id=?', (term_id,))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                if conn:
                    conn.close()
                print(f"Error deleting term: {e}")
                return False
    
    def get_all_terms(self):
        """Retrieve all slang terms from the database."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, term, definition, example, category, date_added, source, polish, pronunciation
                FROM slang_terms
                ORDER BY date_added DESC
            ''')
            
            terms = cursor.fetchall()
            conn.close()
            
            return terms
    
    def get_term_by_id(self, term_id):
        """Get a specific term by ID."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, term, definition, example, category, date_added, source, polish, pronunciation
                FROM slang_terms
                WHERE id = ?
            ''', (term_id,))
            
            term = cursor.fetchone()
            conn.close()
            
            return term
    
    def search_terms(self, search_query):
        """Search for terms matching the query."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, term, definition, example, category, date_added, source, polish, pronunciation
                FROM slang_terms
                WHERE term LIKE ? OR definition LIKE ? OR example LIKE ? OR polish LIKE ?
                ORDER BY date_added DESC
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
            
            terms = cursor.fetchall()
            conn.close()
            
            return terms
    
    def add_search_history(self, search_term, result_count):
        """Record a search in the history."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO search_history (search_term, result_count)
                VALUES (?, ?)
            ''', (search_term, result_count))
            
            conn.commit()
            conn.close()
    
    def get_database_stats(self):
        """Get statistics about the database."""
        with self._lock:
            conn = self._get_connection()
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
    
    def mark_location_searched(self, source_type, source_identifier, terms_found=0):
        """Mark a location/source as searched."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO searched_locations (source_type, source_identifier, search_date, terms_found)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                ''', (source_type, source_identifier, terms_found))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                if conn:
                    conn.close()
                print(f"Error marking location searched: {e}")
                return False
    
    def is_location_searched(self, source_type, source_identifier):
        """Check if a location has already been searched."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM searched_locations 
                WHERE source_type = ? AND source_identifier = ?
            ''', (source_type, source_identifier))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
    
    def add_to_cache(self, term, definition='', example='', category='', polish='', pronunciation='', source_type='', source_url=''):
        """Add a term to the cache."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO term_cache 
                    (term, definition, example, category, polish, pronunciation, source_type, source_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (term, definition, example, category, polish, pronunciation, source_type, source_url))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                if conn:
                    conn.close()
                print(f"Error adding to cache: {e}")
                return False
    
    def get_cached_term(self, term):
        """Get a term from cache if it exists."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT term, definition, example, category, polish, pronunciation, source_type, source_url
                FROM term_cache
                WHERE term = ? COLLATE NOCASE
            ''', (term,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result
    
    def mark_cache_added_to_db(self, term):
        """Mark a cached term as added to the main database."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE term_cache SET added_to_database = 1
                    WHERE term = ? COLLATE NOCASE
                ''', (term,))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                if conn:
                    conn.close()
                print(f"Error marking cache as added: {e}")
                return False
    
    def get_uncached_terms_count(self):
        """Get count of cached terms not yet added to database."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM term_cache WHERE added_to_database = 0')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
