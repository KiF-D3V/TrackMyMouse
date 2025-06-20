# gui/builders/tab_builder.py

import tkinter as tk
from tkinter import ttk
import logging
import importlib
from typing import Dict, Any

from core.service_locator import service_locator

# Import des onglets statiques
from gui.today_tab import TodayTab
from gui.settings_tab import SettingsTab
from gui.about_tab import AboutTab

logger = logging.getLogger(__name__)

class TabBuilder:
    """
    Spécialiste de la construction et de l'ajout des onglets au notebook principal.
    Centralise toute la logique de création des onglets.
    """
    def __init__(self, notebook: ttk.Notebook):
        """
        Initialise le builder avec le widget notebook parent.
        """
        self.notebook = notebook
        self.config_manager = service_locator.get_service("config_manager")
        self.language_manager = service_locator.get_service("language_manager")
        self.tab_references: Dict[str, Any] = {}

    def build_all(self) -> Dict[str, Any]:
        """
        Orchestre la création de tous les onglets et les retourne.
        """
        logger.info("Début de la construction des onglets via TabBuilder...")
        
        self._build_static_tabs_start()
        self._build_optional_tabs()
        self._build_static_tabs_end()
        
        logger.info("Construction des onglets terminée.")
        return self.tab_references

    def _add_tab(self, instance: ttk.Frame, title_key: str, default_text: str, ref_key: str = ""):
        """Méthode utilitaire pour ajouter un onglet au notebook."""
        tab_title = self.language_manager.get_text(title_key, default_text)
        self.notebook.add(instance, text=tab_title)
        if ref_key:
            self.tab_references[ref_key] = instance

    def _build_static_tabs_start(self):
        """Construit les onglets statiques du début (ex: Aujourd'hui)."""
        logger.debug("Construction de l'onglet 'Aujourd'hui'.")
        today_instance = TodayTab(self.notebook)
        self._add_tab(today_instance, 'today_tab_title', 'Today', 'today')

    def _build_optional_tabs(self):
        """Construit dynamiquement les onglets optionnels."""
        logger.debug("Construction des onglets optionnels...")
        optional_tabs = self.config_manager.get_app_config('OPTIONAL_TABS', [])

        for tab_info in optional_tabs:
            if self.config_manager.get_show_tab(tab_info["id"]):
                try:
                    logger.debug(f"Chargement du module pour l'onglet: {tab_info['id']}")
                    module = importlib.import_module(tab_info["module_path"])
                    TabClass = getattr(module, tab_info["class_name"])
                    instance = TabClass(self.notebook)
                    
                    self._add_tab(instance, tab_info["title_key"], tab_info["id"].capitalize(), tab_info["id"])
                    logger.info(f"Onglet '{tab_info['id']}' activé et chargé.")
                except (ImportError, AttributeError) as e:
                    logger.error(f"Impossible de charger l'onglet '{tab_info['id']}': {e}", exc_info=True)

    def _build_static_tabs_end(self):
        """Construit les onglets statiques de fin (ex: Paramètres, À propos)."""
        logger.debug("Construction des onglets 'Paramètres' et 'À propos'.")
        
        settings_instance = SettingsTab(self.notebook)
        self._add_tab(settings_instance, 'settings_tab_title', 'Settings', 'settings')

        about_instance = AboutTab(self.notebook)
        self._add_tab(about_instance, 'about_tab_title', 'About', 'about')