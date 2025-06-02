# managers/stats_manager.py

import sqlite3
import datetime
import os
import time
import threading 
from pynput import mouse
from typing import Optional

# --- Constants ---
DB_FILE = 'data/stats.db'
INACTIVITY_THRESHOLD_SECONDS = 2 # Defines the duration after which mouse inactivity is detected

class StatsManager:
    """
    Manages all mouse and application-related statistics using SQLite for data persistence.
    This class encapsulates all database logic and is designed to be thread-safe.
    It tracks mouse distance, clicks, and user activity time.
    """

    def __init__(self):
        self._conn = None
        self._cursor = None
        self._db_lock = threading.Lock() # Ensures thread-safe access to the database connection
        
        self.today = datetime.date.today().isoformat()
        self.last_mouse_position = None
        self.last_activity_time = time.time()
        self.is_active = True 
        self._stop_tracker = False # Flag to signal the activity tracking thread to stop

        self._connect_db() 
        
        # Load or create today's stats entry into memory for real-time updates
        self._current_day_stats_in_memory = self._get_or_create_todays_entry()
        self._initialize_app_settings()

        # Start the activity tracking thread
        self._activity_tracker_thread = threading.Thread(target=self._run_activity_tracker, daemon=True)
        self._activity_tracker_thread.start()

    def _connect_db(self):
        """Establishes connection to the SQLite database and creates tables if they don't exist."""
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        # Using check_same_thread=False allows multiple threads to use the same connection,
        # but _db_lock is crucial for protecting writes.
        self._conn = sqlite3.connect(DB_FILE, check_same_thread=False) 
        self._conn.row_factory = sqlite3.Row # Allows accessing columns by name
        self._cursor = self._conn.cursor()
        
        with self._db_lock: 
            self._create_tables()

    def _create_tables(self):
        """Creates the necessary database tables (daily_stats and app_settings)."""
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                distance_pixels REAL DEFAULT 0.0,
                left_clicks INTEGER DEFAULT 0,
                right_clicks INTEGER DEFAULT 0,
                middle_clicks INTEGER DEFAULT 0,
                active_time_seconds INTEGER DEFAULT 0,
                inactive_time_seconds INTEGER DEFAULT 0
            )
        ''')
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self._conn.commit() # Commit table creation

    def _initialize_app_settings(self):
        """Ensures essential application settings (like first launch date) are present in DB."""
        with self._db_lock: 
            self._cursor.execute("SELECT value FROM app_settings WHERE key = 'first_launch_date'")
            if self._cursor.fetchone() is None:
                today_str = datetime.date.today().isoformat()
                self._cursor.execute(
                    "INSERT INTO app_settings (key, value) VALUES (?, ?)", 
                    ('first_launch_date', today_str)
                )
                self._conn.commit()

    def _get_or_create_todays_entry(self):
        """
        Retrieves today's stats from the database or creates a new entry if none exists.
        Returns the current day's stats as a dictionary.
        """
        with self._db_lock: 
            self._cursor.execute(
                "SELECT * FROM daily_stats WHERE date = ?", 
                (self.today,)
            )
            row = self._cursor.fetchone()

            if row is None:
                self._cursor.execute(
                    "INSERT INTO daily_stats (date) VALUES (?)", 
                    (self.today,)
                )
                self._conn.commit() 
                # Fetch the newly created row
                self._cursor.execute(
                    "SELECT * FROM daily_stats WHERE date = ?", 
                    (self.today,)
                )
                row = self._cursor.fetchone()
            
            return dict(row) if row else self._get_initial_daily_stats_structure()

    def _update_todays_entry_in_db(self):
        """Updates the current day's stats in the database with in-memory values."""
        with self._db_lock: 
            self._cursor.execute('''
                UPDATE daily_stats
                SET distance_pixels = ?, left_clicks = ?, right_clicks = ?, middle_clicks = ?,
                    active_time_seconds = ?, inactive_time_seconds = ?
                WHERE date = ?
            ''', (
                self._current_day_stats_in_memory['distance_pixels'],
                self._current_day_stats_in_memory['left_clicks'],
                self._current_day_stats_in_memory['right_clicks'],
                self._current_day_stats_in_memory['middle_clicks'],
                self._current_day_stats_in_memory['active_time_seconds'],
                self._current_day_stats_in_memory['inactive_time_seconds'],
                self.today
            ))
            # No commit here; commit is handled by save_changes() which is called externally.

    def _run_activity_tracker(self):
        """
        This thread periodically checks for mouse activity to update active/inactive time.
        It also handles daily rollover of statistics.
        """
        while not self._stop_tracker:
            time.sleep(1) 
            if self._stop_tracker: # Check again after sleep to respond quickly to shutdown signal
                break

            current_time = time.time()
            time_since_last_activity = current_time - self.last_activity_time

            current_date = datetime.date.today().isoformat()
            if self.today != current_date:
                # New day detected: save current day's stats, reset for new day
                self.save_changes() 
                self.today = current_date
                self._current_day_stats_in_memory = self._get_or_create_todays_entry()
                self.last_activity_time = current_time 
                self.is_active = True 

            # Update active/inactive time based on activity threshold
            if time_since_last_activity <= INACTIVITY_THRESHOLD_SECONDS:
                if not self.is_active: # Transition from inactive to active
                    self.is_active = True
                self._current_day_stats_in_memory['active_time_seconds'] += 1
            else:
                if self.is_active: # Transition from active to inactive
                    self.is_active = False
                self._current_day_stats_in_memory['inactive_time_seconds'] += 1

    # --- Public Methods: StatsManager Interface ---

    def increment_click(self, button: mouse.Button):
        """
        Increments the click count for the specified mouse button.
        Handles daily rollover if a new day has started.
        """
        current_date = datetime.date.today().isoformat()
        if self.today != current_date:
            self.save_changes() 
            self.today = current_date
            self._current_day_stats_in_memory = self._get_or_create_todays_entry() 

        if button == mouse.Button.left:
            self._current_day_stats_in_memory['left_clicks'] += 1
        elif button == mouse.Button.right:
            self._current_day_stats_in_memory['right_clicks'] += 1
        elif button == mouse.Button.middle:
            self._current_day_stats_in_memory['middle_clicks'] += 1
        
        self.last_activity_time = time.time() # Mark activity
        self.is_active = True 

    def update_mouse_position(self, x: int, y: int):
        """
        Updates the total mouse distance based on the new position.
        Handles daily rollover and updates last activity time.
        """
        current_time = time.time()
        
        current_date = datetime.date.today().isoformat()
        if self.today != current_date:
            self.save_changes() 
            self.today = current_date
            self._current_day_stats_in_memory = self._get_or_create_todays_entry() 

        if self.last_mouse_position:
            last_x, last_y = self.last_mouse_position
            distance = ((x - last_x)**2 + (y - last_y)**2)**0.5
            self._current_day_stats_in_memory['distance_pixels'] += distance

        self.last_mouse_position = (x, y)
        self.last_activity_time = current_time 
        self.is_active = True 
        
    def get_todays_stats(self) -> dict:
        """Returns the current day's statistics from memory."""
        return self._current_day_stats_in_memory

    def get_global_stats(self) -> dict:
        """
        Calculates and returns aggregated statistics from all recorded days in the database.
        Ensures current day's changes are saved before querying.
        """
        self.save_changes() # Ensure current in-memory stats are persisted before global query

        with self._db_lock: 
            self._cursor.execute('''
                SELECT
                    SUM(distance_pixels) AS total_distance_pixels,
                    SUM(left_clicks) AS total_left_clicks,
                    SUM(right_clicks) AS total_right_clicks,
                    SUM(middle_clicks) AS total_middle_clicks,
                    SUM(active_time_seconds) AS total_active_time_seconds,
                    SUM(inactive_time_seconds) AS total_inactive_time_seconds
                FROM daily_stats
            ''')
            row = self._cursor.fetchone()
            
            # Return 0 for None values if no data exists yet
            return {
                'total_distance_pixels': row['total_distance_pixels'] if row and row['total_distance_pixels'] is not None else 0.0,
                'left_clicks': row['total_left_clicks'] if row and row['total_left_clicks'] is not None else 0,
                'right_clicks': row['total_right_clicks'] if row and row['total_right_clicks'] is not None else 0,
                'middle_clicks': row['total_middle_clicks'] if row and row['total_middle_clicks'] is not None else 0,
                'total_active_time_seconds': row['total_active_time_seconds'] if row and row['total_active_time_seconds'] is not None else 0,
                'total_inactive_time_seconds': row['total_inactive_time_seconds'] if row and row['total_inactive_time_seconds'] is not None else 0,
            }

    def get_first_launch_date(self) -> Optional[str]:
        """Retrieves the recorded first launch date of the application."""
        with self._db_lock: 
            self._cursor.execute("SELECT value FROM app_settings WHERE key = 'first_launch_date'")
            row = self._cursor.fetchone()
            return row['value'] if row else None

    def reset_todays_stats(self):
        """Resets all statistics for the current day to zero."""
        with self._db_lock: 
            self._cursor.execute('''
                UPDATE daily_stats
                SET distance_pixels = 0.0, left_clicks = 0, right_clicks = 0, middle_clicks = 0,
                    active_time_seconds = 0, inactive_time_seconds = 0
                WHERE date = ?
            ''', (self.today,))
            self._conn.commit()
            # Reset in-memory stats to reflect database changes
            self._current_day_stats_in_memory = self._get_initial_daily_stats_structure()

    def reset_global_stats(self):
        """Resets all historical statistics in the database and re-initializes app settings."""
        with self._db_lock: 
            self._cursor.execute("DELETE FROM daily_stats")
            self._cursor.execute("DELETE FROM app_settings WHERE key = 'first_launch_date'")
            
            self._initialize_app_settings() # Re-create first_launch_date for the fresh start

            self._conn.commit()
            # Reset in-memory stats as history is cleared
            self._current_day_stats_in_memory = self._get_initial_daily_stats_structure()

    def save_changes(self):
        """Saves current in-memory statistics for the day to the database."""
        self._update_todays_entry_in_db() 
        with self._db_lock: 
            if self._conn: # Ensure connection is still active
                self._conn.commit()

    def close(self):
        """
        Signals the activity tracker thread to stop, waits for it,
        saves any pending changes, and closes the database connection.
        """
        self._stop_tracker = True # Signal the thread to stop
        if self._activity_tracker_thread.is_alive():
            print("Waiting for activity tracker thread to terminate...") # Keep this for crucial shutdown info
            self._activity_tracker_thread.join(timeout=2.0) # Wait for thread to finish (with timeout)
        
        self.save_changes() 
        with self._db_lock: 
            if self._conn:
                self._conn.close()
                self._conn = None
                self._cursor = None

    def _get_initial_daily_stats_structure(self) -> dict:
        """Returns a dictionary representing the initial state of daily statistics."""
        return {
            'date': self.today,
            'distance_pixels': 0.0,
            'left_clicks': 0,
            'right_clicks': 0,
            'middle_clicks': 0,
            'active_time_seconds': 0,
            'inactive_time_seconds': 0
        }