# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import logging

# --- MODIFICATION : L'import des onglets est maintenant géré par le TabBuilder ---
from gui.builders.tab_builder import TabBuilder

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
        --- MODIFICATION MAJEURE ---
        Délègue la construction et l'ajout de tous les onglets au TabBuilder.
        """
        logger.info("Délégation de la création des onglets au TabBuilder...")
        builder = TabBuilder(self.notebook)
        self.tab_references = builder.build_all()
        
        # On garde une référence directe à l'onglet "Aujourd'hui" si nécessaire
        self.today_tab = self.tab_references.get('today')

    def load_language(self):
        """
        Charge la langue et met à jour dynamiquement le titre et tous les onglets créés.
        """
        logger.debug("Chargement de la langue pour l'ensemble de l'interface.")
        try:
            lang = self.config_manager.get_language() 
            self.language_manager.set_language(lang)

            # Mise à jour du titre de la fenêtre
            self.master.title(f"{self.language_manager.get_text('app_title', 'TrackMyMouse')} v{__version__}")
            
            # --- MODIFICATION : La mise à jour des titres est maintenant gérée par le builder ---
            # Le TabBuilder a déjà ajouté les onglets avec les bons titres.
            # Nous devons maintenant mettre à jour les textes des onglets déjà créés.
            for i, (ref_key, tab_instance) in enumerate(self.tab_references.items()):
                 # On suppose que le builder a stocké la clé de langue quelque part
                 # Pour simplifier, on va se baser sur le mapping du builder
                 # Note: ceci est une simplification, le builder pourrait retourner plus d'infos
                 title_key = f"{ref_key}_tab_title" # ex: today_tab_title
                 default_text = ref_key.capitalize()
                 tab_text = self.language_manager.get_text(title_key, default_text)
                 self.notebook.tab(i, text=tab_text)

                 if hasattr(tab_instance, 'update_widget_texts'):
                    tab_instance.update_widget_texts()
            
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
                # La logique ici est plus simple si on se base sur la référence directe
                if self.today_tab and self.notebook.select() == str(self.today_tab):
                     if hasattr(self.today_tab, 'update_display'):
                        self.today_tab.update_display()

                # Pour les autres onglets dynamiques, une approche plus générale reste nécessaire
                selected_tab_widget = self.notebook.nametowidget(self.notebook.select())
                if hasattr(selected_tab_widget, 'update_display'):
                    selected_tab_widget.update_display()
            except tk.TclError:
                pass
            finally:
                self.master.after(1000, self.update_stats_display_loop)
        else:
            logger.info("Boucle de mise à jour de l'affichage arrêtée.")

    def stop_update_loop(self):
        logger.info("Demande d'arrêt de la boucle de mise à jour.")
        self._running_update_loop = False