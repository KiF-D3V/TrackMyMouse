# gui/today_tab.py

import tkinter as tk
from tkinter import ttk
import datetime
import logging

# Imports des utilitaires et du Service Locator
from utils.service_locator import service_locator
from utils.unit_converter import format_distance, format_seconds_to_hms

class TodayTab(ttk.Frame):
    """
    Onglet de l'interface graphique affichant les statistiques
    du jour et les statistiques globales.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.logger = logging.getLogger(__name__)
        
        # Accès aux services via le Service Locator
        self.language_manager = service_locator.get_service("language_manager")
        self.stats_manager = service_locator.get_service("stats_manager")
        self.preference_manager = service_locator.get_service("preference_manager")

        self._setup_widgets()
        self.logger.info("Onglet 'Aujourd'hui' initialisé.")

    def _setup_widgets(self):
        """
        Configure la disposition et les widgets pour l'onglet.
        """
        self.logger.debug("Configuration des widgets de l'onglet 'Aujourd'hui'.")
        # --- Section "Aujourd'hui" ---
        self.distance_today_label = ttk.Label(self, text="", anchor='w')
        self.distance_today_label.pack(padx=10, pady=(10, 5), fill='x')

        self.clicks_today_label = ttk.Label(self, text="", anchor='w')
        self.clicks_today_label.pack(padx=10, pady=5, fill='x')

        self.activity_today_label = ttk.Label(self, text="", anchor='w')
        self.activity_today_label.pack(padx=10, pady=5, fill='x')

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=5, pady=10)

        # --- Section "Global" ---
        self.start_time_label = ttk.Label(self, text="", anchor='w')
        self.start_time_label.pack(padx=10, pady=5, fill='x')

        self.distance_global_label = ttk.Label(self, text="", anchor='w')
        self.distance_global_label.pack(padx=10, pady=5, fill='x')

        self.clicks_global_label = ttk.Label(self, text="", anchor='w')
        self.clicks_global_label.pack(padx=10, pady=5, fill='x')

        self.activity_global_label = ttk.Label(self, text="", anchor='w')
        self.activity_global_label.pack(padx=10, pady=(5, 10), fill='x')
        self.logger.debug("Widgets de l'onglet 'Aujourd'hui' créés.")

    def update_stats_display(self):
        """
        Met à jour toutes les étiquettes de statistiques de l'onglet
        en récupérant les données les plus récentes.
        """
        try:
            # Récupération des données
            todays_stats = self.stats_manager.get_todays_stats()
            global_stats = self.stats_manager.get_global_stats()
            first_launch_date_iso = self.stats_manager.get_first_launch_date()
            
            # Récupération des préférences
            current_language = self.language_manager.get_current_language()
            dpi = self.preference_manager.get_dpi()
            distance_unit = self.preference_manager.get_distance_unit()
            date_format_from_prefs = self.preference_manager.get_date_format()

            # Préparation des textes formatés
            today_texts = self._prepare_today_stats_texts(todays_stats, dpi, distance_unit, current_language)
            global_texts = self._prepare_global_stats_texts(global_stats, dpi, distance_unit, current_language)
            formatted_start_date = self._get_formatted_first_launch_date(first_launch_date_iso, date_format_from_prefs, current_language)

            # Mise à jour des labels de l'interface
            self.distance_today_label.config(text=today_texts["distance"])
            self.clicks_today_label.config(text=today_texts["clicks"])
            self.activity_today_label.config(text=today_texts["activity"])

            self.start_time_label.config(text=f"{self.language_manager.get_text('started_on', 'Started on:')} {formatted_start_date}")
            self.distance_global_label.config(text=global_texts["distance"])
            self.clicks_global_label.config(text=global_texts["clicks"])
            self.activity_global_label.config(text=global_texts["activity"])

        except Exception as e:
            self.logger.error(f"Erreur majeure lors de la mise à jour de l'affichage des statistiques: {e}", exc_info=True)

    def _prepare_today_stats_texts(self, todays_stats: dict, dpi: float, distance_unit: str, current_language: str) -> dict:
        """
        Prépare les chaînes de caractères formatées pour les statistiques du jour.
        """
        distance_pixels = todays_stats.get('distance_pixels', 0.0)
        formatted_dist, unit = format_distance(distance_pixels, dpi, distance_unit, current_language)
        distance_text = f"{self.language_manager.get_text('todays_distance_label', 'Distance Today:')} {formatted_dist} {unit} ({int(distance_pixels)} pixels)"

        clicks_text = (
            f"{self.language_manager.get_text('todays_clicks_label', 'Clicks Today:')} "
            f"{self.language_manager.get_text('clicks_left_short', 'L')}: {todays_stats.get('left_clicks', 0)} | "
            f"{self.language_manager.get_text('clicks_middle_short', 'M')}: {todays_stats.get('middle_clicks', 0)} | "
            f"{self.language_manager.get_text('clicks_right_short', 'R')}: {todays_stats.get('right_clicks', 0)}"
        )
        
        active_time = format_seconds_to_hms(todays_stats.get('active_time_seconds', 0))
        inactive_time = format_seconds_to_hms(todays_stats.get('inactive_time_seconds', 0))
        activity_text = f"{self.language_manager.get_text('activity_today_label', 'Activity Today:')} {self.language_manager.get_text('active_short', 'Active')} {active_time} | {self.language_manager.get_text('inactive_short', 'Inactive')} {inactive_time}"
        
        return {
            "distance": distance_text,
            "clicks": clicks_text,
            "activity": activity_text
        }

    def _prepare_global_stats_texts(self, global_stats: dict, dpi: float, distance_unit: str, current_language: str) -> dict:
        """
        Prépare les chaînes de caractères formatées pour les statistiques globales.
        """
        total_distance_pixels = global_stats.get('total_distance_pixels', 0.0)
        formatted_dist, unit = format_distance(total_distance_pixels, dpi, distance_unit, current_language)
        distance_text = f"{self.language_manager.get_text('global_distance_label', 'Total Distance:')} {formatted_dist} {unit} ({int(total_distance_pixels)} pixels)"

        clicks_text = (
            f"{self.language_manager.get_text('global_clicks_label', 'Total Clicks:')} "
            f"{self.language_manager.get_text('clicks_left_short', 'L')}: {global_stats.get('left_clicks', 0)} | "
            f"{self.language_manager.get_text('clicks_middle_short', 'M')}: {global_stats.get('middle_clicks', 0)} | "
            f"{self.language_manager.get_text('clicks_right_short', 'R')}: {global_stats.get('right_clicks', 0)}"
        )

        active_time = format_seconds_to_hms(global_stats.get('total_active_time_seconds', 0))
        inactive_time = format_seconds_to_hms(global_stats.get('total_inactive_time_seconds', 0))
        activity_text = f"{self.language_manager.get_text('activity_total_label', 'Total Activity:')} {self.language_manager.get_text('active_short', 'Active')} {active_time} | {self.language_manager.get_text('inactive_short', 'Inactive')} {inactive_time}"
        
        return {
            "distance": distance_text,
            "clicks": clicks_text,
            "activity": activity_text
        }

    def _get_formatted_first_launch_date(self, date_iso: str, date_format_pref: str, current_language: str) -> str:
        """
        Formate la date de premier lancement pour l'affichage.
        """
        if not date_iso:
            self.logger.warning("Date de premier lancement non disponible pour le formatage.")
            return self.language_manager.get_text('unknown_date', "Date inconnue")
        try:
            date_obj = datetime.datetime.fromisoformat(date_iso)
            if current_language == 'fr':
                return date_obj.strftime('%d/%m/%Y %H:%M:%S')
            else:
                return date_obj.strftime(date_format_pref)
        except ValueError as ve:
            self.logger.error(f"Format de date ISO ('{date_iso}') ou de préférence ('{date_format_pref}') invalide: {ve}")
            return date_iso 
    
    def update_widget_texts(self):
        """
        Met à jour les textes des widgets de l'onglet, typiquement après un changement de langue.
        Ici, il suffit de relancer la mise à jour complète des statistiques.
        """
        self.logger.debug("Mise à jour des textes des widgets pour l'onglet 'Aujourd'hui'.")
        self.update_stats_display()