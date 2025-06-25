# gui/builders/tab_builder.py

import tkinter as tk
from tkinter import ttk
import logging
import importlib
import os
from typing import Dict, Any, List

from core.service_locator import service_locator
from utils.paths import get_icon_path

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
        self.icon_references: Dict[str, tk.PhotoImage] = {}

    def build_all(self) -> Dict[str, Any]:
        """
        Orchestre la création de tous les onglets et les retourne.
        """
        logger.info("Début de la construction des onglets via TabBuilder...")

        # Récupération des listes depuis la configuration
        static_tabs_start = self.config_manager.get_app_config('STATIC_TABS_START', [])
        optional_tabs = self.config_manager.get_app_config('OPTIONAL_TABS', [])
        static_tabs_end = self.config_manager.get_app_config('STATIC_TABS_END', [])
        
        # Construction des onglets
        self._build_tabs_from_list(static_tabs_start, is_optional=False)
        self._build_tabs_from_list(optional_tabs, is_optional=True)
        self._build_tabs_from_list(static_tabs_end, is_optional=False)
        
        logger.info("Construction des onglets terminée.")
        return self.tab_references

    def _build_tabs_from_list(self, tab_list: List[Dict[str, Any]], is_optional: bool):
        """
        Méthode générique pour construire une liste d'onglets.
        """
        icons_directory = os.path.dirname(get_icon_path())
        for tab_info in tab_list:
            # Pour les onglets optionnels, on vérifie la préférence
            if is_optional and not self.config_manager.get_show_tab(tab_info["id"]):
                continue

            try:
                # --- Création de l'instance de l'onglet ---
                module = importlib.import_module(tab_info["module_path"])
                TabClass = getattr(module, tab_info["class_name"])
                instance = TabClass(self.notebook)
                
                # --- Gestion de l'icône ---
                icon_image = None
                icon_filename = tab_info.get("icon_filename")
                if icon_filename:
                    icon_path = os.path.join(icons_directory, icon_filename)
                    if os.path.exists(icon_path):
                        # On crée l'objet PhotoImage et on le stocke pour éviter qu'il soit supprimé
                        icon_image = tk.PhotoImage(file=icon_path)
                        self.icon_references[tab_info["id"]] = icon_image
                        logger.debug(f"Icône '{icon_filename}' chargée pour l'onglet '{tab_info['id']}'.")
                    else:
                        logger.warning(f"Fichier icône introuvable : {icon_path}")

                # --- Ajout de l'onglet au Notebook ---
                tab_title = self.language_manager.get_text(tab_info["title_key"], tab_info["id"].capitalize())
                if icon_image:
                    # Si l'image existe, on l'ajoute avec les bonnes options
                    self.notebook.add(instance, text=tab_title, image=icon_image, compound='left')
                else:
                    # Sinon, on ajoute l'onglet sans les options d'image pour éviter le crash
                    self.notebook.add(instance, text=tab_title)
                                
                # On sauvegarde la référence à l'instance de l'onglet
                self.tab_references[tab_info["id"]] = {
                    'instance': instance,
                    'title_key': tab_info['title_key'],
                    'default_text': tab_info['id'].capitalize(),
                    'icon_image': icon_image
                }

                logger.info(f"Onglet '{tab_info['id']}' activé et chargé.")
            except (ImportError, AttributeError) as e:
                logger.error(f"Impossible de charger l'onglet '{tab_info['id']}': {e}", exc_info=True)