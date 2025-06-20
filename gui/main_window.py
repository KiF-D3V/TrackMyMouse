# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import logging
import importlib

# Import onglets toujours affichés
from gui import today_tab
from gui import settings_tab
from gui import about_tab

# Imports de configuration et du Service Locator
from version import __version__
from core.service_locator import service_locator

logger = logging.getLogger(__name__)

class MainWindow(ttk.Frame):
    """
    Fenêtre principale de l'application.
    Assemble dynamiquement les différents onglets en fonction des préférences utilisateur.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        logger.info("Initialisation de MainWindow...")

        self.config_manager = service_locator.get_service("config_manager")
        self.language_manager = service_locator.get_service("language_manager")
        
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
        logger.info("MainWindow initialisée avec succès.")

    def _setup_tabs(self):
        """
        Construit dynamiquement la liste des onglets à afficher
        en lisant le registre central OPTIONAL_TABS.
        """
        logger.info("Configuration dynamique des onglets...")
        
        # --- Onglets principaux (toujours affichés) ---
        today = today_tab.TodayTab(self.notebook)
        self.tabs.append({'instance': today, 'title_key': 'today_tab_title', 'default': 'Today'})
        self.today_tab = today

        # --- MODIFIÉ : Boucle dynamique pour les onglets optionnels ---
        optional_tabs = self.config_manager.get_app_config('OPTIONAL_TABS', [])
        for tab_info in optional_tabs:
            # On utilise la méthode générique pour vérifier si l'onglet doit être affiché
            if self.config_manager.get_show_tab(tab_info["id"]):
                try:
                    # Importation dynamique du module de l'onglet
                    module = importlib.import_module(tab_info["module_path"])
                    # Récupération de la classe de l'onglet depuis le module
                    TabClass = getattr(module, tab_info["class_name"])
                    # Création de l'instance de l'onglet
                    instance = TabClass(self.notebook)
                    
                    self.tabs.append({
                        'instance': instance, 
                        'title_key': tab_info["title_key"], 
                        'default': tab_info["id"].capitalize()
                    })
                    logger.info(f"Onglet '{tab_info['id']}' activé et chargé.")

                except (ImportError, AttributeError) as e:
                    logger.error(f"Impossible de charger l'onglet '{tab_info['id']}': {e}")
        
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
        logger.critical("--- MÉTHODE load_language DE MAIN_WINDOW APPELÉE ---")

        logger.debug("Chargement de la langue pour l'ensemble de l'interface.")
        try:
            lang = self.config_manager.get_language() 
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
            
            logger.info(f"Langue '{lang}' appliquée à l'interface.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la langue: {e}", exc_info=True)

    def update_stats_display_loop(self):
        """
        Boucle périodique qui demande à l'onglet ACTIF de mettre à jour son affichage,
        s'il possède une méthode 'update_display'.
        """
        if self._running_update_loop:
            try:
                # 1. Identifier l'onglet actuellement sélectionné
                selected_tab_widget = self.notebook.nametowidget(self.notebook.select())

                # 2. Vérifier si cet onglet a une méthode 'update_display'
                if hasattr(selected_tab_widget, 'update_display'):
                    # 3. Si oui, l'appeler. Cela fonctionnera pour TodayTab, LevelTab, etc.
                    selected_tab_widget.update_display()

            except tk.TclError:
                # Peut se produire si aucun onglet n'est sélectionné, etc. C'est sans danger.
                pass
            finally:
                # On replanifie le prochain appel dans tous les cas
                self.master.after(1000, self.update_stats_display_loop)
        else:
            logger.info("Boucle de mise à jour de l'affichage arrêtée.")

    def stop_update_loop(self):
        """Signale à la boucle de mise à jour de s'arrêter."""
        logger.info("Demande d'arrêt de la boucle de mise à jour.")
        self._running_update_loop = False