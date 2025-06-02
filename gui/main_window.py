# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import datetime
import locale 
import logging

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
    Gère la fenêtre principale de l'application, y compris ses onglets 
    et l'affichage en temps réel des statistiques.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de MainWindow...")

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

        self._running_update_loop = True 
        self.update_stats_display_loop() 

        self.load_language()
        self.logger.info("MainWindow initialisée avec succès.")


    def load_language(self):
        """
        Charge et applique la langue sélectionnée à tous les éléments pertinents de l'interface graphique.
        """
        self.logger.debug("Chargement de la langue pour l'interface utilisateur.")
        try:
            lang = self.preference_manager.get_language() 
            self.language_manager.set_language(lang)

            self.notebook.tab(0, text=self.language_manager.get_text('today_tab_title', 'Today'))
            self.notebook.tab(1, text=self.language_manager.get_text('settings_tab_title', 'Settings'))
            self.notebook.tab(2, text=self.language_manager.get_text('about_tab_title', 'About'))
            self.master.title(f"{self.language_manager.get_text('app_title', 'Mouse Tracker')} v{__version__}")
            
            if hasattr(self.settings_tab, 'update_widget_texts'):
                self.settings_tab.update_widget_texts()
            if hasattr(self.about_tab, 'update_widget_texts'):
                self.about_tab.update_widget_texts()
            
            self.update_stats_display()
            self.logger.info(f"Langue '{lang}' appliquée à l'interface.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la langue: {e}", exc_info=True)


    def setup_today_tab(self):
        """
        Configure la disposition et les widgets pour l'onglet des statistiques "Aujourd'hui".
        """
        self.logger.debug("Configuration de l'onglet 'Aujourd'hui'.")
        self.distance_today_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.distance_today_label.pack(padx=10, pady=(10,5), fill='x')

        self.clicks_today_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.clicks_today_label.pack(padx=10, pady=5, fill='x')

        self.activity_today_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.activity_today_label.pack(padx=10, pady=5, fill='x')

        ttk.Separator(self.today_tab, orient='horizontal').pack(fill='x', padx=5, pady=10)

        self.start_time_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.start_time_label.pack(padx=10, pady=5, fill='x')

        self.distance_global_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.distance_global_label.pack(padx=10, pady=5, fill='x')

        self.clicks_global_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.clicks_global_label.pack(padx=10, pady=5, fill='x')

        self.activity_global_label = ttk.Label(self.today_tab, text="", anchor='w')
        self.activity_global_label.pack(padx=10, pady=(5,10), fill='x')
        self.logger.debug("Widgets de l'onglet 'Aujourd'hui' configurés.")

    def _prepare_today_stats_texts(self, todays_stats: dict, dpi: float, distance_unit: str, current_language: str) -> dict:
        """
        Prépare les chaînes de caractères formatées pour les statistiques du jour.
        """
        self.logger.debug(f"Préparation des textes pour les stats du jour: {todays_stats}")
        
        distance_pixels = todays_stats.get('distance_pixels', 0.0)
        formatted_dist, unit = format_distance(distance_pixels, dpi, distance_unit, current_language)
        distance_text = f"{self.language_manager.get_text('todays_distance_label', 'Distance Today:')} {formatted_dist} {unit} ({int(distance_pixels)} pixels)"

        # Ordre des clics: Gauche | Milieu | Droite
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
        self.logger.debug(f"Préparation des textes pour les stats globales: {global_stats}")

        total_distance_pixels = global_stats.get('total_distance_pixels', 0.0)
        formatted_dist, unit = format_distance(total_distance_pixels, dpi, distance_unit, current_language)
        distance_text = f"{self.language_manager.get_text('global_distance_label', 'Total Distance:')} {formatted_dist} {unit} ({int(total_distance_pixels)} pixels)"

        # Ordre des clics: Gauche | Milieu | Droite
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
        Formate la date de premier lancement pour l'affichage, 
        en utilisant un format spécifique pour le français.
        """
        if not date_iso:
            self.logger.warning("Date de premier lancement non disponible (None ou vide) pour le formatage.")
            return self.language_manager.get_text('unknown_date', "Date inconnue")
        try:
            date_obj = datetime.datetime.fromisoformat(date_iso)
            # Si la langue est française, utiliser le format JJ/MM/AAAA HH:MM:SS
            if current_language == 'fr':
                self.logger.debug(f"Formatage de la date pour 'fr': {date_obj.strftime('%d/%m/%Y %H:%M:%S')}")
                return date_obj.strftime('%d/%m/%Y %H:%M:%S')
            # Sinon, utiliser le format défini dans les préférences utilisateur
            else:
                self.logger.debug(f"Formatage de la date avec le format des préférences '{date_format_pref}': {date_obj.strftime(date_format_pref)}")
                return date_obj.strftime(date_format_pref)
        except ValueError as ve:
            self.logger.error(f"Format de date ISO ('{date_iso}') ou format de préférence ('{date_format_pref}') invalide: {ve}", exc_info=True)
            return date_iso # Retourne la date brute en cas d'erreur de formatage

    def update_stats_display(self):
        """
        Met à jour toutes les étiquettes de statistiques dans l'onglet "Aujourd'hui".
        """
        try:
            todays_stats = self.stats_manager.get_todays_stats()
            global_stats = self.stats_manager.get_global_stats()
            first_launch_date_iso = self.stats_manager.get_first_launch_date() # Devrait être AAAA-MM-JJTHH:MM:SS
            
            current_language = self.language_manager.get_current_language()
            dpi = self.preference_manager.get_dpi()
            distance_unit = self.preference_manager.get_distance_unit()
            date_format_from_prefs = self.preference_manager.get_date_format()

            today_texts = self._prepare_today_stats_texts(todays_stats, dpi, distance_unit, current_language)
            global_texts = self._prepare_global_stats_texts(global_stats, dpi, distance_unit, current_language)
            formatted_start_date = self._get_formatted_first_launch_date(first_launch_date_iso, date_format_from_prefs, current_language)

            self.distance_today_label.config(text=today_texts["distance"])
            self.clicks_today_label.config(text=today_texts["clicks"])
            self.activity_today_label.config(text=today_texts["activity"])

            self.start_time_label.config(text=f"{self.language_manager.get_text('started_on', 'Started on:')} {formatted_start_date}")
            self.distance_global_label.config(text=global_texts["distance"])
            self.clicks_global_label.config(text=global_texts["clicks"])
            self.activity_global_label.config(text=global_texts["activity"])

        except Exception as e:
            self.logger.error(f"Erreur majeure lors de la mise à jour de l'affichage des statistiques: {e}", exc_info=True)

    def update_stats_display_loop(self):
        """
        Met à jour périodiquement l'affichage des statistiques.
        """
        if self._running_update_loop:
            self.update_stats_display()
            self.master.after(1000, self.update_stats_display_loop)
        else:
            self.logger.info("Boucle de mise à jour de l'affichage des statistiques arrêtée.")

    def stop_update_loop(self):
        """Signale à la boucle de mise à jour de l'affichage de s'arrêter."""
        self.logger.info("Demande d'arrêt de la boucle de mise à jour de l'affichage.")
        self._running_update_loop = False