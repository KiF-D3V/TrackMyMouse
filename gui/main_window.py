# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import logging

# --- MODIFIÉ: Import de tous les onglets, y compris le nouveau ---
from gui import today_tab
from gui import history_tab
from gui import records_tab # AJOUT
from gui import settings_tab
from gui import about_tab

# Imports de configuration et du Service Locator
from version import __version__
from utils.service_locator import service_locator

class MainWindow(ttk.Frame):
    """
    Fenêtre principale de l'application.
    Assemble dynamiquement les différents onglets en fonction des préférences utilisateur.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de MainWindow...")

        self.language_manager = service_locator.get_service("language_manager")
        self.preference_manager = service_locator.get_service("preference_manager") 

        self.master.title(f"{self.language_manager.get_text('app_title', 'TrackMyMouse')} v{__version__}")
        self.master.resizable(True, True)

        self.style = ttk.Style(self.master)
        self.style.theme_use('clam')

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # --- MODIFIÉ: La création des onglets est maintenant dans une méthode dédiée ---
        self.tabs = [] # Va stocker les informations sur les onglets à afficher
        self._setup_tabs()

        # Démarrage de la boucle de rafraîchissement des statistiques
        self._running_update_loop = True 
        self.update_stats_display_loop() 

        # Chargement initial de la langue (qui met aussi à jour les titres des onglets)
        self.load_language()
        self.logger.info("MainWindow initialisée avec succès.")

    def _setup_tabs(self):
        """
        Construit dynamiquement la liste des onglets à afficher
        en fonction des préférences de l'utilisateur.
        """
        self.logger.info("Configuration dynamique des onglets...")
        
        # --- Onglets principaux (toujours affichés) ---
        today = today_tab.TodayTab(self.notebook)
        self.tabs.append({'instance': today, 'title_key': 'today_tab_title', 'default': 'Today'})
        self.today_tab = today # Garde une référence directe pour la boucle de mise à jour

        # --- Onglets optionnels ---
        if self.preference_manager.get_show_history_tab():
            history = history_tab.HistoryTab(self.notebook)
            self.tabs.append({'instance': history, 'title_key': 'history_tab_title', 'default': 'History'})
            self.logger.info("Onglet 'Historique' activé.")

        if self.preference_manager.get_show_records_tab():
            records = records_tab.RecordsTab(self.notebook)
            self.tabs.append({'instance': records, 'title_key': 'records_tab_title', 'default': 'Records'})
            self.logger.info("Onglet 'Records' activé.")

        # --- Onglets de fin (toujours affichés) ---
        settings = settings_tab.SettingsTab(self.notebook)
        self.tabs.append({'instance': settings, 'title_key': 'settings_tab_title', 'default': 'Settings'})
        
        about = about_tab.AboutTab(self.notebook)
        self.tabs.append({'instance': about, 'title_key': 'about_tab_title', 'default': 'About'})

        # Ajout physique des onglets au notebook
        for tab_info in self.tabs:
            tab_text = self.language_manager.get_text(tab_info['title_key'], tab_info['default'])
            self.notebook.add(tab_info['instance'], text=tab_text)

    def load_language(self):
        """
        Charge la langue et met à jour dynamiquement le titre et tous les onglets créés.
        """
        # --- AJOUT: Ligne de test ---
        self.logger.critical("--- MÉTHODE load_language DE MAIN_WINDOW APPELÉE ---")

        self.logger.debug("Chargement de la langue pour l'ensemble de l'interface.")
        try:
            lang = self.preference_manager.get_language() 
            self.language_manager.set_language(lang)

            # Mise à jour du titre de la fenêtre
            self.master.title(f"{self.language_manager.get_text('app_title', 'TrackMyMouse')} v{__version__}")
            
            # --- MODIFIÉ: Boucle dynamique pour mettre à jour les onglets ---
            for i, tab_info in enumerate(self.tabs):
                # Met à jour le titre de l'onglet
                tab_text = self.language_manager.get_text(tab_info['title_key'], tab_info['default'])
                self.notebook.tab(i, text=tab_text)
                
                # Demande à l'onglet de mettre à jour son propre contenu
                if hasattr(tab_info['instance'], 'update_widget_texts'):
                    tab_info['instance'].update_widget_texts()
            
            self.logger.info(f"Langue '{lang}' appliquée à l'interface.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la langue: {e}", exc_info=True)

    def update_stats_display_loop(self):
        """
        Boucle périodique qui demande à l'onglet 'Aujourd'hui' de
        mettre à jour son affichage des statistiques.
        """
        if self._running_update_loop:
            # La boucle ne concerne que l'onglet 'Aujourd'hui' qui affiche des données temps réel
            if hasattr(self, 'today_tab'):
                self.today_tab.update_stats_display()
            self.master.after(1000, self.update_stats_display_loop)
        else:
            self.logger.info("Boucle de mise à jour de l'affichage arrêtée.")

    def stop_update_loop(self):
        """Signale à la boucle de mise à jour de s'arrêter."""
        self.logger.info("Demande d'arrêt de la boucle de mise à jour.")
        self._running_update_loop = False