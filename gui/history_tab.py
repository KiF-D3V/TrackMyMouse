# gui/history_tab.py

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any, Optional
import datetime 

# --- AJOUT: Import des constantes de configuration ---
from config.app_config import HISTORY_DAYS_OPTIONS

from utils.service_locator import service_locator
from utils.unit_converter import format_distance, format_seconds_to_hms

class HistoryTab(ttk.Frame):
    """
    Onglet pour afficher les statistiques historiques.
    Permet à l'utilisateur de voir les données des N derniers jours et les records.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de HistoryTab...")

        self.language_manager = service_locator.get_service("language_manager")
        self.stats_manager = service_locator.get_service("stats_manager")
        self.preference_manager = service_locator.get_service("preference_manager")

        self.n_days_var = tk.IntVar(value=HISTORY_DAYS_OPTIONS[0]) # Défaut sur la 1ère option
        self.history_section_visible = tk.BooleanVar(value=False)
        self.records_section_visible = tk.BooleanVar(value=False)

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
        self._update_ui_texts() 
        self.logger.info("HistoryTab initialisé.")

    def _setup_ui(self):
        self.logger.debug("Configuration de l'UI pour HistoryTab.")
        main_content_frame = ttk.Frame(self, padding="10")
        main_content_frame.pack(expand=True, fill="both")
        
        # --- Section Historique ---
        self.last_n_days_frame_toggle = ttk.Frame(main_content_frame)
        self.last_n_days_frame_toggle.pack(fill="x", pady=(0, 5))
        self.toggle_button_text_var = tk.StringVar()
        self.toggle_button = ttk.Button(
            self.last_n_days_frame_toggle, textvariable=self.toggle_button_text_var,
            command=lambda: self._toggle_section('history'), style="Toolbutton"
        )
        self.toggle_button.pack(side="left", padx=(0, 5))
        
        self.history_content_labelframe = ttk.LabelFrame(main_content_frame, text="")
        options_frame = ttk.Frame(self.history_content_labelframe, padding="5")
        options_frame.pack(fill="x", pady=5)
        self.days_option_label = ttk.Label(options_frame, text="")
        self.days_option_label.pack(side="left", padx=(0,10))
        
        # --- MODIFIÉ: Utilise la constante HISTORY_DAYS_OPTIONS ---
        for days in HISTORY_DAYS_OPTIONS:
            rb = ttk.Radiobutton(
                options_frame, text="", variable=self.n_days_var, 
                value=days, command=self.load_historical_data
            )
            setattr(self, f"rb_days_{days}", rb) 
            rb.pack(side="left", padx=5)
            
        self.tree = ttk.Treeview(
            self.history_content_labelframe, columns=self.column_keys, 
            show="headings", height=7
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
        self._apply_history_content_visibility()

        # --- Section Records ---
        self.records_frame_toggle = ttk.Frame(main_content_frame)
        self.records_frame_toggle.pack(fill="x", pady=(10, 5))
        self.records_toggle_button_text_var = tk.StringVar()
        self.records_toggle_button = ttk.Button(
            self.records_frame_toggle, textvariable=self.records_toggle_button_text_var,
            command=lambda: self._toggle_section('records'), style="Toolbutton"
        )
        self.records_toggle_button.pack(side="left", padx=(0, 5))
        
        self.records_content_labelframe = ttk.LabelFrame(main_content_frame, text="")
        records_grid = ttk.Frame(self.records_content_labelframe, padding="10")
        records_grid.pack(fill="x")
        self.record_distance_label_desc = ttk.Label(records_grid, anchor="w")
        self.record_distance_label_desc.grid(row=0, column=0, sticky="w", pady=2)
        self.record_distance_label_value = ttk.Label(records_grid, anchor="w")
        self.record_distance_label_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.record_activity_label_desc = ttk.Label(records_grid, anchor="w")
        self.record_activity_label_desc.grid(row=1, column=0, sticky="w", pady=2)
        self.record_activity_label_value = ttk.Label(records_grid, anchor="w")
        self.record_activity_label_value.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self._apply_records_visibility()

    def _update_ui_texts(self):
        self.logger.debug("Mise à jour des textes pour HistoryTab.")
        # Section Historique
        section_title_hist = self.language_manager.get_text('history_last_n_days_title', "Historique des derniers jours")
        prefix_hist = "[-]" if self.history_section_visible.get() else "[+]"
        self.toggle_button_text_var.set(f"{prefix_hist} {section_title_hist}")
        self.days_option_label.config(text=self.language_manager.get_text('history_show_days_label', "Afficher :"))
        
        # --- MODIFIÉ: Utilise la constante HISTORY_DAYS_OPTIONS ---
        for days_val in HISTORY_DAYS_OPTIONS:
            rb_widget = getattr(self, f"rb_days_{days_val}", None)
            if rb_widget:
                rb_widget.config(text=self.language_manager.get_text(f'history_{days_val}_days', f"{days_val} jours"))
        
        for key in self.column_keys:
            self.tree.heading(key, text=self.language_manager.get_text(self.column_headers_lang_keys[key], self.column_headers_default_text[key]))
        
        # Section Records
        records_section_title = self.language_manager.get_text('records_section_title', "Records")
        records_prefix = "[-]" if self.records_section_visible.get() else "[+]"
        self.records_toggle_button_text_var.set(f"{records_prefix} {records_section_title}")
        self.record_distance_label_desc.config(text=f"{self.language_manager.get_text('record_distance_label', 'Record de distance')} :")
        self.record_activity_label_desc.config(text=f"{self.language_manager.get_text('record_activity_label', 'Record d''activité')} :")
        self.logger.debug("Textes de HistoryTab mis à jour.")

    def _toggle_section(self, section_to_toggle: str):
        self.logger.info(f"Basculement de la section '{section_to_toggle}'.")
        if section_to_toggle == 'history':
            toggled_var, other_var = self.history_section_visible, self.records_section_visible
        elif section_to_toggle == 'records':
            toggled_var, other_var = self.records_section_visible, self.history_section_visible
        else: return
        
        is_opening = not toggled_var.get()
        if is_opening:
            other_var.set(False)
            if section_to_toggle == 'history': self.load_historical_data()
            elif section_to_toggle == 'records': self.load_records_data()
            
        toggled_var.set(is_opening)
        self._apply_history_content_visibility()
        self._apply_records_visibility()
        self._update_ui_texts()
    
    def _apply_history_content_visibility(self):
        if self.history_section_visible.get():
            self.history_content_labelframe.pack(fill="both", expand=True, padx=5, pady=5, after=self.last_n_days_frame_toggle)
        else:
            self.history_content_labelframe.pack_forget()

    def _apply_records_visibility(self):
        if self.records_section_visible.get():
            self.records_content_labelframe.pack(fill="x", padx=5, pady=5, after=self.records_frame_toggle)
        else:
            self.records_content_labelframe.pack_forget()

    # --- NOUVEAU: Méthode d'assistance pour le formatage de la date ---
    def _get_formatted_date(self, date_str: str) -> str:
        """Formate une date ISO (YYYY-MM-DD) en format localisé."""
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            if self.language_manager.get_current_language() == 'fr':
                return date_obj.strftime('%d/%m/%Y')
            return date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            self.logger.warning(f"Format de date invalide reçu: {date_str}")
            return date_str

    def _format_row_for_display(self, db_row: Dict[str, Any]) -> Dict[str, str]:
        # --- MODIFIÉ: Utilise la nouvelle méthode _get_formatted_date ---
        formatted_row = {'date': self._get_formatted_date(db_row.get('date', ''))}
        
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

    def _format_record_for_display(self, record_row: Optional[Dict[str, Any]], metric_type: str) -> str:
        if not record_row: return self.language_manager.get_text('no_record_yet', "Aucun record")
        
        # --- MODIFIÉ: Utilise la nouvelle méthode _get_formatted_date ---
        formatted_date = self._get_formatted_date(record_row.get('date', ''))
        
        if metric_type == 'distance':
            val, unit = format_distance(record_row.get('distance_pixels', 0.0), self.preference_manager.get_dpi(), self.preference_manager.get_distance_unit(), self.language_manager.get_current_language())
            return f"{val} {unit} ({self.language_manager.get_text('on_date', 'le')} {formatted_date})"
        elif metric_type == 'activity':
            formatted_time = format_seconds_to_hms(record_row.get('active_time_seconds', 0))
            return f"{formatted_time} ({self.language_manager.get_text('on_date', 'le')} {formatted_date})"
        return self.language_manager.get_text('unknown_record', "Record inconnu")

    def load_historical_data(self):
        """Charge les données des N derniers jours et les affiche."""
        num_days_to_fetch = self.n_days_var.get()
        self.logger.info(f"Chargement des données historiques pour les {num_days_to_fetch} derniers jours.")
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            historical_data = self.stats_manager.get_last_n_days_stats(num_days_to_fetch)
            if not historical_data:
                self.logger.info("Aucune donnée historique trouvée.")
                self.tree.insert("", "end", values=(self.language_manager.get_text('history_no_data', "Aucune donnée disponible"), "", "", "", "", "", ""))
                return
            for db_row in historical_data:
                display_row = self._format_row_for_display(db_row)
                ordered_values = [display_row.get(key, "") for key in self.column_keys]
                self.tree.insert("", "end", values=ordered_values)
            self.logger.info(f"{len(historical_data)} jours de données historiques chargés.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données historiques: {e}", exc_info=True)
            self.tree.insert("", "end", values=(self.language_manager.get_text('history_load_error', "Erreur de chargement"), "", "", "", "", "", ""))

    def load_records_data(self):
        """Charge les données des records et met à jour les labels."""
        self.logger.info("Chargement des données des records.")
        try:
            dist_record = self.stats_manager.get_record_day_for_distance()
            activity_record = self.stats_manager.get_record_day_for_activity()
            dist_text = self._format_record_for_display(dist_record, 'distance')
            activity_text = self._format_record_for_display(activity_record, 'activity')
            self.record_distance_label_value.config(text=dist_text)
            self.record_activity_label_value.config(text=activity_text)
            self.logger.info("Données des records chargées et affichées.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des records: {e}", exc_info=True)
            error_msg = self.language_manager.get_text('history_load_error', "Erreur de chargement des données")
            self.record_distance_label_value.config(text=error_msg)
            self.record_activity_label_value.config(text=error_msg)

    # --- MODIFIÉ: Renommage pour la cohérence ---
    def update_widget_texts(self):
        """Met à jour les textes de l'onglet lors d'un changement de langue."""
        self.logger.debug("HistoryTab invité à mettre à jour ses textes.")
        self._update_ui_texts()
        if self.history_section_visible.get():
            self.load_historical_data()
        if self.records_section_visible.get():
            self.load_records_data()