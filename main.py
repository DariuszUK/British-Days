#!/usr/bin/env python3
"""
British Days - Main Application
Full GUI application with PNG/GIF/ICO/BMP/JPG assets support
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import sys
import json
import threading
import time
from database import DatabaseManager
from search import SlangSearcher


class AssetLoader:
    """Loads and scales various image formats for GUI."""
    
    def __init__(self, assets_dir='assets'):
        self.assets_dir = assets_dir
        self.cache = {}
    
    def load(self, filename, size=None):
        """Load image file (png, gif, ico, bmp, jpg) and optionally scale."""
        key = f"{filename}_{size}"
        if key in self.cache:
            return self.cache[key]
        
        try:
            path = os.path.join(self.assets_dir, filename)
            img = Image.open(path)
            
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Scale if size specified
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.cache[key] = photo
            return photo
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            return None


class BritishDaysApp:
    """Main application class."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.config = self._load_config()
        
        # Initialize components
        self.db = DatabaseManager()
        self.searcher = SlangSearcher(db_manager=self.db)
        self.assets = AssetLoader()
        
        # Search state
        self.is_searching = False
        self.search_thread = None
        self.search_gif_frame = 0
        
        # Setup window
        self._setup_window()
        
        # Load all assets
        self._load_all_assets()
        
        # Create GUI
        self._create_gui()
        
        # Load initial data
        self.refresh_display()
    
    def _load_config(self):
        """Load configuration."""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'window_title': 'British Days - Slang Collector',
                'data_directory': 'Data'
            }
    
    def _setup_window(self):
        """Setup the main window."""
        self.root.title(self.config.get('window_title', 'British Days'))
        self.root.state('zoomed')  # Full screen
        
        # Set background color
        self.root.configure(bg='#2C3E50')
        
        # Bind keys
        self.root.bind('<Escape>', lambda e: self.root.state('normal'))
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        
        self.is_fullscreen = True
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.root.state('zoomed')
        else:
            self.root.state('normal')
    
    def _load_all_assets(self):
        """Load all GUI assets."""
        # Main images - adjust sizes as needed
        self.img_background = self.assets.load('background.png', (1920, 1080))  # Background: 1920x1080
        self.img_logo = self.assets.load('logo.png', (100, 100))  # Logo: 100x100
        self.img_panel = self.assets.load('panel_main.png', (800, 600))  # Panel: 800x600
        
        # Buttons - 150x50
        self.img_btn_search = self.assets.load('btn_search.png', (150, 50))
        self.img_btn_refresh = self.assets.load('btn_refresh.png', (150, 50))
        self.img_btn_exit = self.assets.load('btn_exit.png', (150, 50))
        
        # Additional UI elements (reuse existing or create placeholders)
        # Icon for window: 32x32
        try:
            icon = self.assets.load('logo.png', (32, 32))
            if icon:
                self.root.iconphoto(True, icon)
        except:
            pass
        
        # Load search progress GIF (animated)
        # For now, we'll use static image and animate manually
        self.img_search_progress = self.assets.load('btn_search.png', (50, 50))  # Reuse: 50x50
        
        # Small icons for buttons: 24x24
        self.img_icon_edit = self.assets.load('btn_refresh.png', (24, 24))  # Reuse as edit icon
        self.img_icon_delete = self.assets.load('btn_exit.png', (24, 24))  # Reuse as delete icon
        self.img_icon_add = self.assets.load('btn_search.png', (24, 24))  # Reuse as add icon
    
    def _create_gui(self):
        """Create the main GUI."""
        # Main canvas with background
        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            bg='#2C3E50'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw background if available
        if self.img_background:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_background)
        
        # ===== HEADER SECTION =====
        # Logo (top-left): 100x100 at position (50, 20)
        if self.img_logo:
            self.canvas.create_image(50, 20, anchor=tk.NW, image=self.img_logo)
        
        # Title text (center-top)
        self.canvas.create_text(
            960, 50,  # Center of 1920px width
            text="🇬🇧 British Days - Kolekcjoner Slangu",
            font=('Arial', 28, 'bold'),
            fill='#ECF0F1'
        )
        
        # Stats label (top-right)
        self.stats_text = self.canvas.create_text(
            1700, 50,
            text="Łącznie: 0 fraz",
            font=('Arial', 14),
            fill='#ECF0F1',
            anchor=tk.E
        )
        
        # ===== LEFT PANEL - CONTROLS =====
        # Panel background: 300x900 at (50, 150)
        panel_left_frame = tk.Frame(self.canvas, bg='#34495E', bd=2, relief=tk.RAISED)
        self.canvas.create_window(50, 150, anchor=tk.NW, window=panel_left_frame, width=320, height=850)
        
        # Control buttons with images
        y_pos = 20
        
        # Search button with icon
        if self.img_btn_search:
            btn_search = tk.Button(
                panel_left_frame,
                image=self.img_btn_search,
                command=self.start_auto_search,
                borderwidth=0,
                cursor='hand2',
                bg='#34495E',
                activebackground='#2C3E50'
            )
            btn_search.place(x=85, y=y_pos)
            y_pos += 70
        
        # Stop button
        if self.img_btn_exit:  # Reuse exit button as stop
            self.btn_stop = tk.Button(
                panel_left_frame,
                image=self.img_btn_exit,
                command=self.stop_search,
                borderwidth=0,
                cursor='hand2',
                bg='#34495E',
                activebackground='#2C3E50',
                state=tk.DISABLED
            )
            self.btn_stop.place(x=85, y=y_pos)
            y_pos += 70
        
        # Separator line
        ttk.Separator(panel_left_frame, orient=tk.HORIZONTAL).place(x=10, y=y_pos, width=300)
        y_pos += 20
        
        # Sort section
        tk.Label(
            panel_left_frame,
            text="Sortuj według:",
            font=('Arial', 12, 'bold'),
            bg='#34495E',
            fg='#ECF0F1'
        ).place(x=10, y=y_pos)
        y_pos += 30
        
        self.sort_var = tk.StringVar(value="date_desc")
        sort_options = [
            ("Najnowsze", "date_desc"),
            ("Najstarsze", "date_asc"),
            ("A-Z", "term_asc"),
            ("Z-A", "term_desc"),
            ("Kategoria", "category")
        ]
        
        for text, value in sort_options:
            rb = tk.Radiobutton(
                panel_left_frame,
                text=text,
                variable=self.sort_var,
                value=value,
                command=self.refresh_display,
                font=('Arial', 11),
                bg='#34495E',
                fg='#ECF0F1',
                selectcolor='#2C3E50',
                activebackground='#34495E',
                activeforeground='#ECF0F1'
            )
            rb.place(x=20, y=y_pos)
            y_pos += 30
        
        y_pos += 10
        ttk.Separator(panel_left_frame, orient=tk.HORIZONTAL).place(x=10, y=y_pos, width=300)
        y_pos += 20
        
        # Search in database
        tk.Label(
            panel_left_frame,
            text="Wyszukaj w bazie:",
            font=('Arial', 12, 'bold'),
            bg='#34495E',
            fg='#ECF0F1'
        ).place(x=10, y=y_pos)
        y_pos += 35
        
        self.search_entry = tk.Entry(
            panel_left_frame,
            font=('Arial', 14),
            bg='#ECF0F1',
            fg='#2C3E50',
            width=25
        )
        self.search_entry.place(x=10, y=y_pos)
        # Real-time search on key release
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_database_realtime())
        y_pos += 40
        
        # Clear search button
        tk.Button(
            panel_left_frame,
            text="Pokaż wszystko",
            command=self.refresh_display,
            font=('Arial', 11),
            bg='#3498DB',
            fg='white',
            cursor='hand2',
            width=22
        ).place(x=10, y=y_pos)
        y_pos += 50
        
        ttk.Separator(panel_left_frame, orient=tk.HORIZONTAL).place(x=10, y=y_pos, width=300)
        y_pos += 20
        
        # Selected term operations
        tk.Label(
            panel_left_frame,
            text="Zaznaczona fraza:",
            font=('Arial', 12, 'bold'),
            bg='#34495E',
            fg='#ECF0F1'
        ).place(x=10, y=y_pos)
        y_pos += 35
        
        # Edit button with icon
        btn_edit = tk.Button(
            panel_left_frame,
            text=" ✏️ Edytuj",
            command=self.edit_selected,
            font=('Arial', 11),
            bg='#F39C12',
            fg='white',
            cursor='hand2',
            width=22,
            image=self.img_icon_edit if self.img_icon_edit else None,
            compound=tk.LEFT
        )
        btn_edit.place(x=10, y=y_pos)
        y_pos += 40
        
        # Delete button with icon
        btn_delete = tk.Button(
            panel_left_frame,
            text=" 🗑️ Usuń",
            command=self.delete_selected,
            font=('Arial', 11),
            bg='#E74C3C',
            fg='white',
            cursor='hand2',
            width=22,
            image=self.img_icon_delete if self.img_icon_delete else None,
            compound=tk.LEFT
        )
        btn_delete.place(x=10, y=y_pos)
        y_pos += 50
        
        ttk.Separator(panel_left_frame, orient=tk.HORIZONTAL).place(x=10, y=y_pos, width=300)
        
        # Exit button at bottom
        if self.img_btn_exit:
            btn_exit = tk.Button(
                panel_left_frame,
                image=self.img_btn_exit,
                command=self.exit_app,
                borderwidth=0,
                cursor='hand2',
                bg='#34495E',
                activebackground='#2C3E50'
            )
            btn_exit.place(x=85, y=780)
        
        # ===== CENTER/RIGHT PANEL - DATA DISPLAY =====
        # Main data panel: 1500x850 at (400, 150)
        panel_right_frame = tk.Frame(self.canvas, bg='#ECF0F1', bd=2, relief=tk.RAISED)
        self.canvas.create_window(400, 150, anchor=tk.NW, window=panel_right_frame, width=1450, height=850)
        
        # Title for data section
        tk.Label(
            panel_right_frame,
            text="📚 Zapisane frazy brytyjskiego slangu",
            font=('Arial', 18, 'bold'),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(pady=10)
        
        # Treeview for terms
        tree_frame = tk.Frame(panel_right_frame, bg='#ECF0F1')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('term', 'definition', 'example', 'category', 'polish', 'pronunciation')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=18)
        
        self.tree.heading('#0', text='ID')
        self.tree.heading('term', text='Fraza')
        self.tree.heading('definition', text='Definicja (EN)')
        self.tree.heading('example', text='Przykład')
        self.tree.heading('category', text='Kategoria')
        self.tree.heading('polish', text='Polski')
        self.tree.heading('pronunciation', text='Wymowa')
        
        # Load column widths from config or use defaults
        column_widths = self.config.get('column_widths', {
            '#0': 50,
            'term': 120,
            'definition': 250,
            'example': 200,
            'category': 100,
            'polish': 150,
            'pronunciation': 120
        })
        
        self.tree.column('#0', width=column_widths.get('#0', 50), stretch=False)
        self.tree.column('term', width=column_widths.get('term', 120))
        self.tree.column('definition', width=column_widths.get('definition', 250))
        self.tree.column('example', width=column_widths.get('example', 200))
        self.tree.column('category', width=column_widths.get('category', 100))
        self.tree.column('polish', width=column_widths.get('polish', 150))
        self.tree.column('pronunciation', width=column_widths.get('pronunciation', 120))
        
        # Bind column resize event to save widths
        self.tree.bind('<ButtonRelease-1>', self._on_column_resize)
        
        # Configure style
        style = ttk.Style()
        style.configure('Treeview', font=('Arial', 16), rowheight=35)
        style.configure('Treeview.Heading', font=('Arial', 14, 'bold'))
        
        # Tag for highlighting search results
        self.tree.tag_configure('highlight', background='#FFEB3B')
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # ===== PROGRESS/LOG SECTION =====
        log_label_frame = tk.LabelFrame(
            panel_right_frame,
            text="🔍 Postęp wyszukiwania i komunikaty",
            font=('Arial', 12, 'bold'),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        log_label_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        # Progress GIF area (animated icon)
        self.progress_canvas = tk.Canvas(log_label_frame, width=50, height=50, bg='#ECF0F1', highlightthickness=0)
        self.progress_canvas.pack(side=tk.LEFT, padx=10)
        
        if self.img_search_progress:
            self.progress_icon = self.progress_canvas.create_image(25, 25, image=self.img_search_progress)
        
        # Log text area
        log_text_frame = tk.Frame(log_label_frame, bg='#ECF0F1')
        log_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
            log_text_frame,
            font=('Consolas', 11),
            height=6,
            bg='#FAFAFA',
            fg='#2C3E50',
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(log_label_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Initial log message
        self.log_message("Aplikacja gotowa do działania! Kliknij 'Search' aby znaleźć nowe frazy.", "INFO")
    
    def log_message(self, message, level="INFO"):
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        
        if level == "SUCCESS":
            prefix = "✓"
            color = "green"
        elif level == "ERROR":
            prefix = "✗"
            color = "red"
        elif level == "DUPLICATE":
            prefix = "⊗"
            color = "orange"
        else:
            prefix = "ℹ"
            color = "blue"
        
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def _on_column_resize(self, event):
        """Handle column resize and save widths to config."""
        # Save current column widths
        column_widths = {}
        for col in ['#0', 'term', 'definition', 'example', 'category', 'polish', 'pronunciation']:
            column_widths[col] = self.tree.column(col, 'width')
        
        # Update config
        self.config['column_widths'] = column_widths
        
        # Save to file
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving column widths: {e}")
    
    def animate_search_icon(self):
        """Animate the search progress icon (rotate)."""
        if self.is_searching and hasattr(self, 'progress_icon'):
            # Simple rotation animation
            self.search_gif_frame = (self.search_gif_frame + 10) % 360
            # Note: For actual rotation, you'd need to rotate the image
            # For now, just show it's active
            self.root.after(100, self.animate_search_icon)
    
    def start_auto_search(self):
        """Start automatic search in background thread."""
        if self.is_searching:
            return
        
        self.is_searching = True
        if hasattr(self, 'btn_stop'):
            self.btn_stop.config(state=tk.NORMAL)
        self.progress_bar.start(10)
        
        self.log_message("🚀 Rozpoczynam automatyczne wyszukiwanie nowych fraz...", "INFO")
        self.animate_search_icon()
        
        self.search_thread = threading.Thread(target=self._auto_search_worker, daemon=True)
        self.search_thread.start()
    
    def _increment_search_failure(self, reason, message, level="DUPLICATE"):
        """Helper method to increment failure counter and log consistently."""
        self.root.after(0, self.log_message, message, level)
        return 1  # Return 1 to increment the counter
    
    def _auto_search_worker(self):
        """Worker thread for automatic searching."""
        search_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 10
        
        # No limit on max_searches - keep searching until stopped or too many failures
        while self.is_searching and consecutive_failures < max_consecutive_failures:
            try:
                existing_terms = {term[1].lower() for term in self.db.get_all_terms()}
                result = self.searcher.search_new_slang()
                
                if result:
                    term_lower = result['term'].lower()
                    
                    if term_lower in existing_terms:
                        consecutive_failures += self._increment_search_failure(
                            "duplicate",
                            f"Duplikat: '{result['term']}' już jest w bazie danych",
                            "DUPLICATE"
                        )
                    else:
                        success, term_id = self.db.add_term(
                            result['term'],
                            result['definition'],
                            result.get('example', ''),
                            result.get('category', 'slang'),
                            result.get('source', 'internet'),
                            result.get('polish', ''),
                            result.get('pronunciation', '')
                        )
                        
                        if success:
                            self.root.after(0, self.log_message, 
                                          f"✅ Dodano: '{result['term']}' - {result['definition'][:40]}...", 
                                          "SUCCESS")
                            self.root.after(0, self.refresh_display)
                            search_count += 1
                            consecutive_failures = 0  # Reset on success
                        else:
                            consecutive_failures += self._increment_search_failure(
                                "add_failed",
                                f"Nie udało się dodać: '{result['term']}'",
                                "ERROR"
                            )
                else:
                    consecutive_failures += self._increment_search_failure(
                        "no_result",
                        "Brak wyników z wyszukiwania",
                        "ERROR"
                    )
                
                time.sleep(0.8)
                
            except Exception as e:
                consecutive_failures += self._increment_search_failure(
                    "exception",
                    f"Błąd: {str(e)}",
                    "ERROR"
                )
                time.sleep(1)
        
        self.root.after(0, self._search_completed, search_count)
    
    def _search_completed(self, count):
        """Called when search is completed."""
        self.is_searching = False
        self.progress_bar.stop()
        if hasattr(self, 'btn_stop'):
            self.btn_stop.config(state=tk.DISABLED)
        self.log_message(f"🎉 Wyszukiwanie zakończone! Dodano {count} nowych fraz.", "SUCCESS")
    
    def stop_search(self):
        """Stop the automatic search."""
        if self.is_searching:
            self.is_searching = False
            self.log_message("⏹ Zatrzymywanie wyszukiwania...", "INFO")
    
    def search_database_realtime(self):
        """Real-time search in database with highlighting."""
        query = self.search_entry.get().strip().lower()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all terms
        if not query:
            terms = self.db.get_all_terms()
            highlight = False
        else:
            terms = self.db.search_terms(query)
            highlight = True
        
        # Apply sorting
        terms = self._sort_terms(terms)
        
        # Populate tree with highlighting
        for term in terms:
            term_id, term_name, definition, example, category, date_added, source, polish, pronunciation = term
            
            item_id = self.tree.insert('', tk.END, text=str(term_id), 
                           values=(term_name, definition, example or '', category or '', 
                                   polish or '', pronunciation or ''))
            
            # Highlight if search active
            if highlight and query:
                if (query in term_name.lower() or 
                    query in (definition or '').lower() or 
                    query in (example or '').lower() or
                    query in (polish or '').lower()):
                    self.tree.item(item_id, tags=('highlight',))
        
        # Update stats
        self._update_stats()
    
    def _sort_terms(self, terms):
        """Sort terms based on selected option."""
        sort_option = self.sort_var.get()
        if sort_option == "date_asc":
            return sorted(terms, key=lambda x: x[5])
        elif sort_option == "date_desc":
            return sorted(terms, key=lambda x: x[5], reverse=True)
        elif sort_option == "term_asc":
            return sorted(terms, key=lambda x: x[1].lower())
        elif sort_option == "term_desc":
            return sorted(terms, key=lambda x: x[1].lower(), reverse=True)
        elif sort_option == "category":
            return sorted(terms, key=lambda x: (x[4] or '', x[1].lower()))
        return terms
    
    def refresh_display(self):
        """Refresh the terms display."""
        self.search_entry.delete(0, tk.END)
        self.search_database_realtime()
    
    def _update_stats(self):
        """Update statistics display."""
        stats = self.db.get_database_stats()
        self.canvas.itemconfig(self.stats_text, text=f"Łącznie: {stats['total_terms']} fraz")
    
    def edit_selected(self):
        """Edit selected term."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Proszę zaznaczyć frazę do edycji.")
            return
        
        item = self.tree.item(selected[0])
        term_id = int(item['text'])
        term_data = self.db.get_term_by_id(term_id)
        
        if term_data:
            EditDialog(self.root, self.db, term_data, self.refresh_display)
    
    def delete_selected(self):
        """Delete selected term."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Proszę zaznaczyć frazę do usunięcia.")
            return
        
        item = self.tree.item(selected[0])
        term_id = int(item['text'])
        term_name = item['values'][0]
        
        if messagebox.askyesno("Potwierdzenie usunięcia", f"Usunąć frazę '{term_name}'?"):
            self.db.delete_term(term_id)
            self.log_message(f"🗑️ Usunięto: '{term_name}'", "INFO")
            self.refresh_display()
    
    def exit_app(self):
        """Exit the application."""
        if self.is_searching:
            self.stop_search()
            time.sleep(0.5)
        
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz wyjść z aplikacji?"):
            self.root.quit()


class EditDialog:
    """Dialog for editing a term."""
    
    def __init__(self, parent, db, term_data, refresh_callback):
        self.db = db
        self.term_data = term_data
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edytuj frazę")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#ECF0F1')
        
        term_id, term, definition, example, category, date_added, source, polish, pronunciation = term_data
        
        frame = tk.Frame(self.dialog, bg='#ECF0F1', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Term
        tk.Label(frame, text="Fraza:", font=('Arial', 12, 'bold'), bg='#ECF0F1').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.term_entry = tk.Entry(frame, font=('Arial', 12), width=50)
        self.term_entry.insert(0, term)
        self.term_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Definition
        tk.Label(frame, text="Definicja (EN):", font=('Arial', 12, 'bold'), bg='#ECF0F1').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.def_text = tk.Text(frame, font=('Arial', 12), width=50, height=3)
        self.def_text.insert('1.0', definition or '')
        self.def_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Polish translation
        tk.Label(frame, text="Polski:", font=('Arial', 12, 'bold'), bg='#ECF0F1').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.polish_text = tk.Text(frame, font=('Arial', 12), width=50, height=3)
        self.polish_text.insert('1.0', polish or '')
        self.polish_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Example
        tk.Label(frame, text="Przykład:", font=('Arial', 12, 'bold'), bg='#ECF0F1').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.ex_text = tk.Text(frame, font=('Arial', 12), width=50, height=2)
        self.ex_text.insert('1.0', example or '')
        self.ex_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Pronunciation
        tk.Label(frame, text="Wymowa:", font=('Arial', 12, 'bold'), bg='#ECF0F1').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.pron_entry = tk.Entry(frame, font=('Arial', 12), width=50)
        self.pron_entry.insert(0, pronunciation or '')
        self.pron_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Category
        tk.Label(frame, text="Kategoria:", font=('Arial', 12, 'bold'), bg='#ECF0F1').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cat_entry = tk.Entry(frame, font=('Arial', 12), width=50)
        self.cat_entry.insert(0, category or '')
        self.cat_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Buttons
        btn_frame = tk.Frame(frame, bg='#ECF0F1')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Zapisz", command=self.save, font=('Arial', 12), 
                 bg='#27AE60', fg='white', width=15, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Anuluj", command=self.dialog.destroy, font=('Arial', 12),
                 bg='#95A5A6', fg='white', width=15, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        frame.columnconfigure(1, weight=1)
    
    def save(self):
        """Save changes."""
        term_id = self.term_data[0]
        term = self.term_entry.get().strip()
        definition = self.def_text.get('1.0', tk.END).strip()
        polish = self.polish_text.get('1.0', tk.END).strip()
        example = self.ex_text.get('1.0', tk.END).strip()
        pronunciation = self.pron_entry.get().strip()
        category = self.cat_entry.get().strip()
        
        if not term:
            messagebox.showerror("Błąd", "Fraza nie może być pusta!")
            return
        
        self.db.update_term(term_id, term, definition, example, category, polish, pronunciation)
        self.refresh_callback()
        self.dialog.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = BritishDaysApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
