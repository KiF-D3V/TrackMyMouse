# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import datetime
import locale 

# Importe les onglets
from gui import settings_tab
from gui import about_tab

# Imports de configuration et utilitaires
from config.version import __version__
from utils.unit_converter import format_distance, format_seconds_to_hms 

# Service Locator pour accéder aux managers
from utils.service_locator import service_locator

class MainWindow(ttk.Frame):
    """
    Manages the main application window, including its tabs and real-time statistics display.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.language_manager = service_locator.get_service("language_manager")
        self.stats_manager = service_locator.get_service("stats_manager")
        self.preference_manager = service_locator.get_service("preference_manager") 

        self.master.title(f"{self.language_manager.get_text('app_title', 'Mouse Tracker')} v{__version__}")
        self.master.resizable(True, True)

        self.style = ttk.Style(self.master)
        self.style.theme_use('clam')

        self.notebook = ttk.Notebook(self)

        self.today_tab = ttk.Frame(self.notebook)
        self.settings_tab = settings_tab.SettingsTab(self.notebook) 
        self.about_tab = about_tab.AboutTab(self.notebook)

        self.notebook.add(self.today_tab, text=self.language_manager.get_text('today_tab_title', 'Today'))
        self.notebook.add(self.settings_tab, text=self.language_manager.get_text('settings_tab_title', 'Settings'))
        self.notebook.add(self.about_tab, text=self.language_manager.get_text('about_tab_title', 'About'))

        self.setup_today_tab()

        self.notebook.pack(expand=True, fill='both')

        # Control flag for the update loop
        self._running = True # NEW: Flag to control the update loop

        # Start the display refresh loop
        self.update_stats_display_loop() 

        self.load_language()

    def load_language(self):
        """Loads and applies the selected language to all relevant GUI elements."""
        lang = self.preference_manager.get_language() 
        self.language_manager.set_language(lang)
        self.notebook.tab(0, text=self.language_manager.get_text('today_tab_title', 'Today'))
        self.notebook.tab(1, text=self.language_manager.get_text('settings_tab_title', 'Settings'))
        self.notebook.tab(2, text=self.language_manager.get_text('about_tab_title', 'About'))
        self.master.title(f"{self.language_manager.get_text('app_title', 'Mouse Tracker')} v{__version__}")
        self.settings_tab.update_screen_dimension_labels()
        self.settings_tab.update_widget_texts()
        self.about_tab.update_widget_texts()
        self.update_stats_display() 

    def setup_today_tab(self):
        """Sets up the layout and widgets for the 'Today' statistics tab."""
        # "Today" section
        self.distance_today_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.distance_today_label.pack(padx=10, pady=5, fill='x')

        self.clicks_today_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.clicks_today_label.pack(padx=10, pady=5, fill='x')

        self.activity_today_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.activity_today_label.pack(padx=10, pady=5, fill='x')

        # Separator
        ttk.Separator(self.today_tab, orient='horizontal').pack(fill='x', padx=5, pady=5)

        # "Total" (Global) section
        self.start_time_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.start_time_label.pack(padx=10, pady=5, fill='x')

        self.distance_global_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.distance_global_label.pack(padx=10, pady=5, fill='x')

        self.clicks_global_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.clicks_global_label.pack(padx=10, pady=5, fill='x')

        self.activity_global_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.activity_global_label.pack(padx=10, pady=5, fill='x')

    def update_stats_display(self):
        """
        Updates all statistics labels in the 'Today' tab with current data.
        """
        todays_stats = self.stats_manager.get_todays_stats()
        global_stats = self.stats_manager.get_global_stats()
        first_launch_date_iso = self.stats_manager.get_first_launch_date()
        current_language = self.language_manager.get_current_language()

        dpi = self.preference_manager.get_dpi()
        distance_unit = self.preference_manager.get_distance_unit()

        # Today's stats
        left_clicks_today = todays_stats.get('left_clicks', 0)
        right_clicks_today = todays_stats.get('right_clicks', 0)
        middle_clicks_today = todays_stats.get('middle_clicks', 0) 
        distance_pixels_today = todays_stats.get('distance_pixels', 0.0)
        active_time_today = todays_stats.get('active_time_seconds', 0)
        inactive_time_today = todays_stats.get('inactive_time_seconds', 0)

        # Global stats
        left_clicks_global = global_stats.get('left_clicks', 0)
        right_clicks_global = global_stats.get('right_clicks', 0)
        middle_clicks_global = global_stats.get('middle_clicks', 0) 
        total_distance_pixels_global = global_stats.get('total_distance_pixels', 0.0)
        active_time_global = global_stats.get('total_active_time_seconds', 0)
        inactive_time_global = global_stats.get('total_inactive_time_seconds', 0)

        # Format distances and times using imported utility functions
        formatted_distance_today, unit_today = format_distance(distance_pixels_today, dpi, distance_unit, current_language)
        formatted_distance_global, unit_global = format_distance(total_distance_pixels_global, dpi, distance_unit, current_language)

        formatted_active_time_today = format_seconds_to_hms(active_time_today)
        formatted_inactive_time_today = format_seconds_to_hms(inactive_time_today)
        formatted_active_time_global = format_seconds_to_hms(active_time_global)
        formatted_inactive_time_global = format_seconds_to_hms(inactive_time_global)

        # Date format from PreferenceManager
        date_format = self.preference_manager.get_date_format() 

        try:
            first_launch_date = datetime.datetime.fromisoformat(first_launch_date_iso).strftime(date_format)
        except (ValueError, TypeError):
            first_launch_date = first_launch_date_iso # Fallback if ISO format is incorrect or missing

        # Update labels
        self.distance_today_label.config(
            text=f"{self.language_manager.get_text('todays_distance_label', 'Distance Today:')} {formatted_distance_today} {unit_today} ({int(distance_pixels_today)} pixels)"
        )
        self.clicks_today_label.config(
            text=f"{self.language_manager.get_text('clicks', 'Clicks')} = {left_clicks_today} {self.language_manager.get_text('clicks_left_short', 'L')} | {right_clicks_today} {self.language_manager.get_text('clicks_right_short', 'R')} | {middle_clicks_today} {self.language_manager.get_text('clicks_middle_short', 'M')}"
        )
        self.activity_today_label.config(
            text=f"{self.language_manager.get_text('activity_today_label', 'Activity Today:')} {self.language_manager.get_text('active_short', 'Active')} {formatted_active_time_today} | {self.language_manager.get_text('inactive_short', 'Inactive')} {formatted_inactive_time_today}"
        )

        # Start date label before global stats
        self.start_time_label.config(
            text=f"{self.language_manager.get_text('started_on', 'Started on:')} {first_launch_date}"
        )
        self.distance_global_label.config(
            text=f"{self.language_manager.get_text('global_distance_label', 'Total Distance:')} {formatted_distance_global} {unit_global} ({int(total_distance_pixels_global)} pixels)"
        )
        self.clicks_global_label.config(
            text=f"{self.language_manager.get_text('clicks', 'Clicks')} = {left_clicks_global} {self.language_manager.get_text('clicks_left_short', 'L')} | {right_clicks_global} {self.language_manager.get_text('clicks_right_short', 'R')} | {middle_clicks_global} {self.language_manager.get_text('clicks_middle_short', 'M')}"
        )
        self.activity_global_label.config(
            text=f"{self.language_manager.get_text('activity_total_label', 'Total Activity:')} {self.language_manager.get_text('active_short', 'Active')} {formatted_active_time_global} | {self.language_manager.get_text('inactive_short', 'Inactive')} {formatted_inactive_time_global}"
        )

    def update_stats_display_loop(self):
        """
        Periodically updates the statistics display in the 'Today' tab.
        This loop stops when the application is shutting down.
        """
        if self._running: # Only continue if the flag is True
            self.update_stats_display()
            self.master.after(1000, self.update_stats_display_loop)

    def stop_update_loop(self): # NEW: Method to stop the update loop
        """Signals the statistics display loop to stop."""
        self._running = False