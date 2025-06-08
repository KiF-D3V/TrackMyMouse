# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import logging

# --- AJOUT: Import du nouvel onglet "Aujourd'hui" ---
from gui import today_tab
# Imports des autres onglets
from gui import settings_tab
from gui import about_tab
from gui import history_tab

# Imports de configuration et du Service Locator
from version import __version__
from utils.service_locator import service_locator

class MainWindow(ttk.Frame):
    """
    Fenêtre principale de l'application.
    Assemble les différents onglets (Today, History, Settings, About)
    et orchestre les mises à jour globales comme le changement de langue
    et la boucle de rafraîchissement des données.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de MainWindow...")

        self.language_manager = service_locator.get_service("language_manager")
        self.preference_manager = service_locator.get_service("preference_manager") 

        self.master.title(f"{self.language_manager.get_text('app_title', 'Mouse Tracker')} v{__version__}")
        self.master.resizable(True, True)

        self.style = ttk.Style(self.master)
        self.style.theme_use('clam')

        self.notebook = ttk.Notebook(self)

        # --- MODIFIÉ: Instanciation des onglets depuis leurs propres modules ---
        self.today_tab = today_tab.TodayTab(self.notebook)
        self.history_tab = history_tab.HistoryTab(self.notebook)
        self.settings_tab = settings_tab.SettingsTab(self.notebook) 
        self.about_tab = about_tab.AboutTab(self.notebook)

        # Ajout des onglets au notebook
        self.notebook.add(self.today_tab, text=self.language_manager.get_text('today_tab_title', 'Today'))
        self.notebook.add(self.history_tab, text=self.language_manager.get_text('history_tab_title', 'History'))
        self.notebook.add(self.settings_tab, text=self.language_manager.get_text('settings_tab_title', 'Settings'))
        self.notebook.add(self.about_tab, text=self.language_manager.get_text('about_tab_title', 'About'))

        self.notebook.pack(expand=True, fill='both')

        # Démarrage de la boucle de rafraîchissement des statistiques
        self._running_update_loop = True 
        self.update_stats_display_loop() 

        # Chargement initial de la langue
        self.load_language()
        self.logger.info("MainWindow initialisée avec succès.")

    def load_language(self):
        """
        Charge et applique la langue à la fenêtre principale et délègue
        la mise à jour du texte à chaque onglet enfant.
        """
        self.logger.debug("Chargement de la langue pour l'ensemble de l'interface.")
        try:
            lang = self.preference_manager.get_language() 
            self.language_manager.set_language(lang)

            # Mise à jour des textes gérés par MainWindow (titre, noms d'onglets)
            self.master.title(f"{self.language_manager.get_text('app_title', 'TrackMyMouse')} v{__version__}")
            self.notebook.tab(0, text=self.language_manager.get_text('today_tab_title', 'Today'))
            self.notebook.tab(1, text=self.language_manager.get_text('history_tab_title', 'History')) 
            self.notebook.tab(2, text=self.language_manager.get_text('settings_tab_title', 'Settings')) 
            self.notebook.tab(3, text=self.language_manager.get_text('about_tab_title', 'About'))
            
            # --- MODIFIÉ: L'appel à history_tab utilise maintenant le nom de méthode cohérent ---
            self.today_tab.update_widget_texts()
            self.history_tab.update_widget_texts() 
            self.settings_tab.update_widget_texts()
            self.about_tab.update_widget_texts()
            
            self.logger.info(f"Langue '{lang}' appliquée à l'interface.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la langue: {e}", exc_info=True)

    def update_stats_display_loop(self):
        """
        Boucle périodique qui demande à l'onglet 'Aujourd'hui' de
        mettre à jour son affichage des statistiques.
        """
        if self._running_update_loop:
            # --- MODIFIÉ: Délégation de la mise à jour à l'onglet concerné ---
            self.today_tab.update_stats_display()
            self.master.after(1000, self.update_stats_display_loop)
        else:
            self.logger.info("Boucle de mise à jour de l'affichage arrêtée.")

    def stop_update_loop(self):
        """Signale à la boucle de mise à jour de s'arrêter."""
        self.logger.info("Demande d'arrêt de la boucle de mise à jour.")
        self._running_update_loop = False
