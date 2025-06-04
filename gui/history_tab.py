# gui/history_tab.py

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any
import datetime 

from utils.service_locator import service_locator
from utils.unit_converter import format_distance, format_seconds_to_hms

class HistoryTab(ttk.Frame):
    """
    Onglet pour afficher les statistiques historiques.
    Permet à l'utilisateur de voir les données des N derniers jours.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de HistoryTab...")

        self.language_manager = service_locator.get_service("language_manager")
        self.stats_manager = service_locator.get_service("stats_manager")
        self.preference_manager = service_locator.get_service("preference_manager")

        self.n_days_var = tk.IntVar(value=7) 
        self.history_section_visible = tk.BooleanVar(value=True)

        self.column_keys = [
            "date", "distance", "clicks_left", "clicks_middle", "clicks_right", 
            "active_time", "inactive_time"
        ]
        self.column_headers_lang_keys = {
            "date": "history_col_date",
            "distance": "history_col_distance",
            "clicks_left": "history_col_clicks_left",
            "clicks_middle": "history_col_clicks_middle",
            "clicks_right": "history_col_clicks_right",
            "active_time": "history_col_active",
            "inactive_time": "history_col_inactive"
        }
        self.column_headers_default_text = {
            "date": "Date", "distance": "Distance", "clicks_left": "Clics G.",
            "clicks_middle": "Clics M.", "clicks_right": "Clics D.",
            "active_time": "Temps Actif", "inactive_time": "Temps Inactif"
        }

        self._setup_ui()
        self._update_ui_texts() 
        self.load_historical_data() 
        self.logger.info("HistoryTab initialisé.")

    def _setup_ui(self):
        self.logger.debug("Configuration de l'UI pour HistoryTab.")
        main_content_frame = ttk.Frame(self, padding="10")
        main_content_frame.pack(expand=True, fill="both")
        
        self.last_n_days_frame_toggle = ttk.Frame(main_content_frame)
        self.last_n_days_frame_toggle.pack(fill="x", pady=(0, 5))

        self.toggle_button_text_var = tk.StringVar()
        self.toggle_button = ttk.Button(
            self.last_n_days_frame_toggle,
            textvariable=self.toggle_button_text_var,
            command=self._toggle_history_content_visibility,
            style="Toolbutton"
        )
        self.toggle_button.pack(side="left", padx=(0, 5))
        
        self.history_content_labelframe = ttk.LabelFrame(main_content_frame, text="")
        
        options_frame = ttk.Frame(self.history_content_labelframe, padding="5")
        options_frame.pack(fill="x", pady=5)

        self.days_option_label = ttk.Label(options_frame, text="")
        self.days_option_label.pack(side="left", padx=(0,10))

        days_options = [7, 14, 30] 
        for days in days_options:
            rb = ttk.Radiobutton(
                options_frame, 
                text="", 
                variable=self.n_days_var, 
                value=days,
                command=self.load_historical_data
            )
            setattr(self, f"rb_days_{days}", rb) 
            rb.pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            self.history_content_labelframe, 
            columns=self.column_keys, 
            show="headings",
            height=10
        )
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)

        # --- MODIFICATION DES LARGEURS DE COLONNES ---
        # Définir les largeurs souhaitées
        column_widths = {
            "date": 72,  
            "distance": 72,
            "clicks_left": 50,
            "clicks_middle": 50,
            "clicks_right": 50,
            "active_time": 75, # Pour HH:MM:SS
            "inactive_time": 75 # Pour HH:MM:SS
        }
        # Valeur par défaut si une clé n'est pas dans column_widths (par exemple, 70)
        default_other_column_width = 70 

        for key in self.column_keys:
            # Utiliser la largeur spécifique si définie, sinon la largeur par défaut générale
            width = column_widths.get(key, default_other_column_width)
            self.tree.column(key, width=width, minwidth=width, anchor="w" if key == "date" else "center", stretch=tk.NO)
            # Ajout de minwidth=width et stretch=tk.NO pour un meilleur contrôle
            self.tree.heading(key, text=self.column_headers_default_text[key]) 
        # --- FIN DE LA MODIFICATION DES LARGEURS ---

        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self._apply_history_content_visibility()

    def _update_ui_texts(self):
        self.logger.debug("Mise à jour des textes pour HistoryTab.")
        section_title = self.language_manager.get_text('history_last_n_days_title', "Historique des derniers jours")
        prefix = "[-]" if self.history_section_visible.get() else "[+]"
        self.toggle_button_text_var.set(f"{prefix} {section_title}")

        self.days_option_label.config(text=self.language_manager.get_text('history_show_days_label', "Afficher :"))
        for days_val in [7, 14, 30]:
            rb_widget = getattr(self, f"rb_days_{days_val}", None)
            if rb_widget:
                rb_widget.config(text=self.language_manager.get_text(f'history_{days_val}_days', f"{days_val} jours"))
        
        for key in self.column_keys:
            header_text = self.language_manager.get_text(
                self.column_headers_lang_keys[key], 
                self.column_headers_default_text[key]
            )
            self.tree.heading(key, text=header_text)
        self.logger.debug("Textes de HistoryTab mis à jour.")

    def _toggle_history_content_visibility(self):
        self.history_section_visible.set(not self.history_section_visible.get())
        self.logger.info(f"Visibilité de la section historique basculée à: {self.history_section_visible.get()}")
        self._apply_history_content_visibility()
        self._update_ui_texts() 

    def _apply_history_content_visibility(self):
        if self.history_section_visible.get():
            self.history_content_labelframe.pack(fill="both", expand=True, padx=5, pady=5, after=self.last_n_days_frame_toggle)
        else:
            self.history_content_labelframe.pack_forget()

    def _format_row_for_display(self, db_row: Dict[str, Any]) -> Dict[str, str]:
        formatted_row = {}
        date_str = db_row.get('date', '')
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            if self.language_manager.get_current_language() == 'fr':
                formatted_row['date'] = date_obj.strftime('%d/%m/%Y')
            else: 
                formatted_row['date'] = date_obj.strftime('%Y-%m-%d') 
        except ValueError:
            formatted_row['date'] = date_str
            self.logger.warning(f"Format de date invalide pour l'historique: {date_str}")

        distance_pixels = db_row.get('distance_pixels', 0.0)
        dpi = self.preference_manager.get_dpi()
        unit_system = self.preference_manager.get_distance_unit()
        lang = self.language_manager.get_current_language()
        dist_val, dist_unit = format_distance(distance_pixels, dpi, unit_system, lang)
        formatted_row['distance'] = f"{dist_val} {dist_unit}"
        
        formatted_row['clicks_left'] = str(db_row.get('left_clicks', 0))
        formatted_row['clicks_middle'] = str(db_row.get('middle_clicks', 0))
        formatted_row['clicks_right'] = str(db_row.get('right_clicks', 0))
        
        formatted_row['active_time'] = format_seconds_to_hms(db_row.get('active_time_seconds', 0))
        formatted_row['inactive_time'] = format_seconds_to_hms(db_row.get('inactive_time_seconds', 0))
        
        return formatted_row

    def load_historical_data(self):
        num_days_to_fetch = self.n_days_var.get()
        self.logger.info(f"Chargement des données historiques pour les {num_days_to_fetch} derniers jours.")
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            historical_data: List[Dict[str, Any]] = self.stats_manager.get_last_n_days_stats(num_days_to_fetch)
            if not historical_data:
                self.logger.info("Aucune donnée historique trouvée pour la période sélectionnée.")
                self.tree.insert("", "end", values=(self.language_manager.get_text('history_no_data', "Aucune donnée disponible"), "", "", "", "", "", ""))
                return
            for db_row in historical_data:
                display_row = self._format_row_for_display(db_row)
                ordered_values = [display_row.get(key, "") for key in self.column_keys]
                self.tree.insert("", "end", values=ordered_values)
            self.logger.info(f"{len(historical_data)} jours de données historiques chargés et affichés.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement ou de l'affichage des données historiques: {e}", exc_info=True)
            self.tree.insert("", "end", values=(self.language_manager.get_text('history_load_error', "Erreur de chargement des données"), "", "", "", "", "", ""))

    def update_language(self):
        self.logger.debug("HistoryTab invité à mettre à jour sa langue.")
        self._update_ui_texts()