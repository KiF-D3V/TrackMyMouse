# gui/records_tab.py

import tkinter as tk
from tkinter import ttk
import logging
import datetime
from typing import Dict, Any, Optional

from utils.service_locator import service_locator
from utils.unit_converter import format_distance, format_seconds_to_hms

logger = logging.getLogger(__name__)

class RecordsTab(ttk.Frame):
    """
    Onglet de l'interface graphique dédié à l'affichage des records
    de l'utilisateur (plus grande distance, plus longue activité).
    """
    def __init__(self, master=None):
        super().__init__(master)
        logger.info("Initialisation de RecordsTab...")

        # Accès aux managers via le Service Locator
        self.config_manager = service_locator.get_service("config_manager")
        self.language_manager = service_locator.get_service("language_manager")
        self.stats_manager = service_locator.get_service("stats_manager")

        self._setup_ui()
        # Appel initial pour définir les textes et charger les données
        self.update_widget_texts() 
        logger.info("RecordsTab initialisé.")

    def _setup_ui(self):
        """
        Configure la disposition et les widgets pour l'onglet des records.
        """
        logger.debug("Configuration de l'UI pour RecordsTab.")
        
        # Un frame principal pour avoir un padding autour du contenu
        main_content_frame = ttk.Frame(self, padding="10")
        main_content_frame.pack(expand=True, fill="both")

        # Le LabelFrame sert de conteneur principal avec un titre
        self.records_content_labelframe = ttk.LabelFrame(main_content_frame, text="") # Le texte sera défini par update_widget_texts
        self.records_content_labelframe.pack(fill="x", padx=5, pady=5)

        # Un grid pour aligner proprement les labels de description et de valeur
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

    def update_widget_texts(self):
        """
        Met à jour les textes des widgets de l'onglet et recharge les données.
        Appelée lors d'un changement de langue.
        """
        logger.debug("RecordsTab invité à mettre à jour ses textes.")
        
        # Mettre à jour le titre du LabelFrame
        records_section_title = self.language_manager.get_text('records_section_title', "Records")
        self.records_content_labelframe.config(text=records_section_title)

        # Mettre à jour les labels de description
        self.record_distance_label_desc.config(text=f"{self.language_manager.get_text('record_distance_label', 'Record de distance')} :")
        self.record_activity_label_desc.config(text=f"{self.language_manager.get_text('record_activity_label', 'Record d''activité')} :")
        
        # Recharger les données pour refléter les changements de langue dans les valeurs
        self.load_records_data()

    def load_records_data(self):
        """Charge les données des records et met à jour les labels de valeur."""
        logger.info("Chargement des données des records.")
        try:
            dist_record = self.stats_manager.get_record_day_for_distance()
            activity_record = self.stats_manager.get_record_day_for_activity()

            dist_text = self._format_record_for_display(dist_record, 'distance')
            activity_text = self._format_record_for_display(activity_record, 'activity')
            
            self.record_distance_label_value.config(text=dist_text)
            self.record_activity_label_value.config(text=activity_text)
            logger.info("Données des records chargées et affichées.")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des records: {e}", exc_info=True)
            error_msg = self.language_manager.get_text('history_load_error', "Erreur de chargement des données")
            self.record_distance_label_value.config(text=error_msg)
            self.record_activity_label_value.config(text=error_msg)

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

    def _format_record_for_display(self, record_row: Optional[Dict[str, Any]], metric_type: str) -> str:
        """Formate une ligne de record pour l'affichage."""
        if not record_row:
            return self.language_manager.get_text('no_record_yet', "Aucun record")
        
        formatted_date = self._get_formatted_date(record_row.get('date', ''))
        
        if metric_type == 'distance':
            val, unit = format_distance(
                record_row.get('distance_pixels', 0.0), 
                self.config_manager.get_dpi(), 
                self.config_manager.get_distance_unit(), 
                self.language_manager.get_current_language()
            )
            return f"{val} {unit} ({self.language_manager.get_text('on_date', 'le')} {formatted_date})"
        
        elif metric_type == 'activity':
            formatted_time = format_seconds_to_hms(record_row.get('active_time_seconds', 0))
            return f"{formatted_time} ({self.language_manager.get_text('on_date', 'le')} {formatted_date})"
            
        return self.language_manager.get_text('unknown_record', "Record inconnu")