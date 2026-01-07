#!/usr/bin/env python3
"""
British Days - Main Application
A single-window application that searches for British slang terms and stores them in a database.
GUI built entirely from PNG elements.
"""
import tkinter as tk
import PIL
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import json
from database import DatabaseManager
from search import SlangSearcher


class BritishDaysApp:
    """Main application class."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.config = self._load_config()
        
        # Initialize database and searcher
        self.db = DatabaseManager()
        self.searcher = SlangSearcher()
        
        # Setup window
        self._setup_window()
        
        # Load PNG assets
        self.images = {}
        self._load_assets()
        
        # Create GUI
        self._create_gui()
        
        # Perform initial search on startup
        self.auto_search_on_startup()
    
    def _load_config(self):
        """Load configuration."""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'window_title': 'British Days - Slang Collector',
                'window_width': 800,
                'window_height': 600,
                'data_directory': 'data'  # Default data directory
            }
    
    def _setup_window(self):
        """Setup the main window."""
        self.root.title(self.config.get('window_title', 'British Days'))
        
        # Set window size
        width = self.config.get('window_width', 800)
        height = self.config.get('window_height', 600)
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.resizable(False, False)
    
    def _load_assets(self):
        """Load all PNG assets."""
        assets_dir = 'assets'
        
        try:
            # Load background
            bg_img = Image.open(os.path.join(assets_dir, 'background.png'))
            self.images['background'] = ImageTk.PhotoImage(bg_img)
            
            # Load buttons
            btn_search = Image.open(os.path.join(assets_dir, 'btn_search.png'))
            self.images['btn_search'] = ImageTk.PhotoImage(btn_search)
            
            btn_refresh = Image.open(os.path.join(assets_dir, 'btn_refresh.png'))
            self.images['btn_refresh'] = ImageTk.PhotoImage(btn_refresh)
            
            btn_exit = Image.open(os.path.join(assets_dir, 'btn_exit.png'))
            self.images['btn_exit'] = ImageTk.PhotoImage(btn_exit)
            
            # Load panel
            panel_img = Image.open(os.path.join(assets_dir, 'panel_main.png'))
            self.images['panel'] = ImageTk.PhotoImage(panel_img)
            
            # Load logo
            logo_img = Image.open(os.path.join(assets_dir, 'logo.png'))
            self.images['logo'] = ImageTk.PhotoImage(logo_img)
            
        except Exception as e:
            print(f"Error loading assets: {e}")
            messagebox.showerror("Error", f"Failed to load PNG assets: {e}")
    
    def _create_gui(self):
        """Create the GUI using PNG elements."""
        # Main canvas with background
        self.canvas = tk.Canvas(
            self.root,
            width=800,
            height=600,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Set background
        if 'background' in self.images:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.images['background'])
        
        # Add logo
        if 'logo' in self.images:
            self.canvas.create_image(50, 70, anchor=tk.NW, image=self.images['logo'])
        
        # Add title text
        self.canvas.create_text(
            400, 30,
            text="British Days - Slang Collector",
            font=('Arial', 24, 'bold'),
            fill='white'
        )
        
        # Add panel for content
        if 'panel' in self.images:
            self.canvas.create_image(50, 180, anchor=tk.NW, image=self.images['panel'])
        
        # Text area for displaying slang
        self.text_area = tk.Text(
            self.root,
            width=80,
            height=18,
            font=('Arial', 10),
            bg='#ECF0F1',
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.canvas.create_window(60, 190, anchor=tk.NW, window=self.text_area)
        
        # Add buttons using PNG images
        if 'btn_search' in self.images:
            btn_search = tk.Button(
                self.root,
                image=self.images['btn_search'],
                command=self.search_new_term,
                borderwidth=0,
                cursor='hand2'
            )
            self.canvas.create_window(200, 520, anchor=tk.NW, window=btn_search)
        
        if 'btn_refresh' in self.images:
            btn_refresh = tk.Button(
                self.root,
                image=self.images['btn_refresh'],
                command=self.refresh_display,
                borderwidth=0,
                cursor='hand2'
            )
            self.canvas.create_window(370, 520, anchor=tk.NW, window=btn_refresh)
        
        if 'btn_exit' in self.images:
            btn_exit = tk.Button(
                self.root,
                image=self.images['btn_exit'],
                command=self.exit_app,
                borderwidth=0,
                cursor='hand2'
            )
            self.canvas.create_window(540, 520, anchor=tk.NW, window=btn_exit)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=('Arial', 9),
            bg='#2C3E50',
            fg='white',
            anchor=tk.W
        )
        self.canvas.create_window(10, 575, anchor=tk.NW, window=self.status_label)
        
        # Display initial content
        self.refresh_display()
    
    def auto_search_on_startup(self):
        """Automatically search for a new term on startup."""
        self.update_status("Searching for new British slang...")
        self.root.update()
        
        # Perform search
        result = self.searcher.search_new_slang()
        
        if result:
            # Add to database
            success, term_id = self.db.add_term(
                result['term'],
                result['definition'],
                result.get('example', ''),
                result.get('category', 'slang'),
                result.get('source', 'internet')
            )
            
            if success:
                self.update_status(f"Added new term: {result['term']}")
                self.refresh_display()
            else:
                self.update_status(f"Term already exists: {result['term']}")
        else:
            self.update_status("Search failed")
    
    def search_new_term(self):
        """Search for a new British slang term."""
        self.update_status("Searching for new slang...")
        
        # Perform search
        result = self.searcher.search_new_slang()
        
        if result:
            # Add to database
            success, term_id = self.db.add_term(
                result['term'],
                result['definition'],
                result.get('example', ''),
                result.get('category', 'slang'),
                result.get('source', 'internet')
            )
            
            if success:
                messagebox.showinfo(
                    "New Term Found!",
                    f"Term: {result['term']}\n\n"
                    f"Definition: {result['definition']}\n\n"
                    f"Example: {result.get('example', 'N/A')}"
                )
                self.update_status(f"Added: {result['term']}")
                self.refresh_display()
            else:
                messagebox.showwarning(
                    "Duplicate Term",
                    f"The term '{result['term']}' already exists in the database."
                )
                self.update_status(f"Duplicate: {result['term']}")
        else:
            messagebox.showerror("Error", "Failed to find a new term.")
            self.update_status("Search failed")
    
    def refresh_display(self):
        """Refresh the display with all terms from database."""
        self.update_status("Refreshing display...")
        
        # Clear text area
        self.text_area.delete(1.0, tk.END)
        
        # Get all terms
        terms = self.db.get_all_terms()
        
        # Display statistics
        stats = self.db.get_database_stats()
        self.text_area.insert(tk.END, f"=== British Slang Database ===\n")
        self.text_area.insert(tk.END, f"Total Terms: {stats['total_terms']}\n")
        self.text_area.insert(tk.END, f"Database: {stats['database_path']}\n")
        self.text_area.insert(tk.END, f"\n{'='*60}\n\n")
        
        # Display terms
        if terms:
            for i, term in enumerate(terms, 1):
                term_id, term_name, definition, example, category, date_added, source = term
                
                self.text_area.insert(tk.END, f"{i}. {term_name.upper()}\n")
                self.text_area.insert(tk.END, f"   Category: {category}\n")
                self.text_area.insert(tk.END, f"   Definition: {definition}\n")
                if example:
                    self.text_area.insert(tk.END, f"   Example: \"{example}\"\n")
                self.text_area.insert(tk.END, f"   Added: {date_added} | Source: {source}\n")
                self.text_area.insert(tk.END, f"\n")
        else:
            self.text_area.insert(tk.END, "No terms in database yet. Click 'Search' to find new slang!\n")
        
        self.update_status("Display updated")
    
    def update_status(self, message):
        """Update the status bar."""
        self.status_label.config(text=message)
        self.root.update()
    
    def exit_app(self):
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = BritishDaysApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
