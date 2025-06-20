# gui/history_tab.py

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any
import datetime 

from core.service_locator import service_locator
from utils.unit_converter import format_distance, format_seconds_to_hms

logger = logging.getLogger(__name__)

class HistoryTab(ttk.Frame):
    """
    Onglet de l'interface graphique affichant l'historique des données
    sous forme de tableau pour une période sélectionnable.
    """
    def __init__(self, master=None):
        super().__init__(master)
        logger.info("Initialisation de HistoryTab (simplifié)...")

        self.config_manager = service_locator.get_service("config_manager")
        self.language_manager = service_locator.get_service("language_manager")
        self.stats_manager = service_locator.get_service("stats_manager")
        
        history_options = self.config_manager.get_app_config('HISTORY_DAYS_OPTIONS', [7, 14, 30])
        self.n_days_var = tk.IntVar(value=history_options[0])

        self.column_keys = [
            "date", "distance", "clicks_left", "clicks_middle", "clicks_right", 
            "active_time", "inactive_time"
        ]
        self.column_headers_lang_keys = {
            "date": "history_col_date", "distance": "history_col_distance",
            "clicks_left": "history_col_clicks_left", "clicks_middle": "history_col_clicks_middle",
            "clicks_right": "history_col_clicks_right", "active_time": "history_col_active",
            "inactive_time": "history_col_inactive"
        }
        self.column_headers_default_text = {
            "date": "Date", "distance": "Distance", "clicks_left": "Clics G.",
            "clicks_middle": "Clics M.", "clicks_right": "Clics D.",
            "active_time": "Temps Actif", "inactive_time": "Temps Inactif"
        }

        self._setup_ui()
        self.update_widget_texts() 
        logger.info("HistoryTab initialisé.")

    def _setup_ui(self):
        """
        Configure l'UI simplifiée, sans section dépliante.
        """
        logger.debug("Configuration de l'UI pour HistoryTab (simplifié).")
        main_content_frame = ttk.Frame(self, padding="10")
        main_content_frame.pack(expand=True, fill="both")
        
        history_labelframe = ttk.LabelFrame(main_content_frame, text="") 
        history_labelframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.history_labelframe = history_labelframe # Garde une référence

        options_frame = ttk.Frame(history_labelframe, padding="5")
        options_frame.pack(fill="x", pady=5)
        self.days_option_label = ttk.Label(options_frame, text="")
        self.days_option_label.pack(side="left", padx=(0,10))
        
        history_options = self.config_manager.get_app_config('HISTORY_DAYS_OPTIONS', [])
        for days in history_options:
            rb = ttk.Radiobutton(
                options_frame, text="", variable=self.n_days_var, 
                value=days, command=self.load_historical_data
            )
            setattr(self, f"rb_days_{days}", rb) 
            rb.pack(side="left", padx=5)
            
        self.tree = ttk.Treeview(
            history_labelframe, columns=self.column_keys, 
            show="headings", height=10
        )
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        
        column_widths = { "date": 72, "distance": 72, "clicks_left": 50, "clicks_middle": 50, "clicks_right": 50, "active_time": 75, "inactive_time": 75 }
        for key in self.column_keys:
            width = column_widths.get(key, 70)
            self.tree.column(key, width=width, minwidth=width, anchor="w" if key == "date" else "center", stretch=tk.NO)
            self.tree.heading(key, text=self.column_headers_default_text[key]) 
        
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def update_widget_texts(self):
        """Met à jour les textes des widgets et recharge les données."""
        logger.debug("HistoryTab invité à mettre à jour ses textes.")
        
        title = self.language_manager.get_text('history_last_n_days_title', "Historique des derniers jours")
        self.history_labelframe.config(text=title)
        
        self.days_option_label.config(text=self.language_manager.get_text('history_show_days_label', "Afficher :"))
        
        history_options = self.config_manager.get_app_config('HISTORY_DAYS_OPTIONS', [])
        for days_val in history_options:
            rb_widget = getattr(self, f"rb_days_{days_val}", None)
            if rb_widget:
                rb_widget.config(text=self.language_manager.get_text(f'history_{days_val}_days', f"{days_val} jours"))
        
        for key in self.column_keys:
            self.tree.heading(key, text=self.language_manager.get_text(self.column_headers_lang_keys[key], self.column_headers_default_text[key]))
            
        self.load_historical_data()

    def load_historical_data(self):
        """Charge les données des N derniers jours et les affiche dans le tableau."""
        num_days_to_fetch = self.n_days_var.get()
        logger.info(f"Chargement des données historiques pour les {num_days_to_fetch} derniers jours.")
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            historical_data = self.stats_manager.get_last_n_days_stats(num_days_to_fetch)
            if not historical_data:
                logger.info("Aucune donnée historique trouvée.")
                self.tree.insert("", "end", values=(self.language_manager.get_text('history_no_data', "Aucune donnée disponible"),))
                return
            for db_row in historical_data:
                display_row = self._format_row_for_display(db_row)
                ordered_values = [display_row.get(key, "") for key in self.column_keys]
                self.tree.insert("", "end", values=ordered_values)
            logger.info(f"{len(historical_data)} jours de données historiques chargés.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données historiques: {e}", exc_info=True)
            self.tree.insert("", "end", values=(self.language_manager.get_text('history_load_error', "Erreur de chargement"),))

    def _get_formatted_date(self, date_str: str) -> str:
        """Formate une date ISO (YYYY-MM-DD) en format localisé."""
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            if self.language_manager.get_current_language() == 'fr':
                return date_obj.strftime('%d/%m/%Y')
            return date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            logger.warning(f"Format de date invalide reçu: {date_str}")
            return date_str

    def _format_row_for_display(self, db_row: Dict[str, Any]) -> Dict[str, str]:
        """Formate une ligne de données pour l'affichage dans le tableau."""
        formatted_row = {'date': self._get_formatted_date(db_row.get('date', ''))}
        
        distance_pixels = db_row.get('distance_pixels', 0.0)
        dpi = self.config_manager.get_dpi()
        unit_system = self.config_manager.get_distance_unit()
        lang = self.language_manager.get_current_language()
        
        dist_val, dist_unit = format_distance(distance_pixels, dpi, unit_system, lang)
        formatted_row['distance'] = f"{dist_val} {dist_unit}"
        formatted_row['clicks_left'] = str(db_row.get('left_clicks', 0))
        formatted_row['clicks_middle'] = str(db_row.get('middle_clicks', 0))
        formatted_row['clicks_right'] = str(db_row.get('right_clicks', 0))
        formatted_row['active_time'] = format_seconds_to_hms(db_row.get('active_time_seconds', 0))
        formatted_row['inactive_time'] = format_seconds_to_hms(db_row.get('inactive_time_seconds', 0))
        return formatted_row