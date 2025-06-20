# gui/settings_tab.py

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable

from core.service_locator import service_locator
from .settings_components.language_settings_frame import LanguageSettingsFrame
from .settings_components.unit_settings_frame import UnitSettingsFrame
from .settings_components.screen_config_frame import ScreenConfigFrame
from .settings_components.features_toggle_frame import FeaturesToggleFrame

class SettingsTab(ttk.Frame):
    """
    Onglet des paramètres.
    Agit comme un conteneur qui assemble les différents composants de paramètres.
    """
    def __init__(self, master=None):
        super().__init__(master)
        
        # --- Dépendances ---
        self.config_manager = service_locator.get_service("config_manager")
        self.language_manager = service_locator.get_service("language_manager")

        # --- Variables d'état partagées ---
        # Cette variable est partagée avec le composant de configuration de l'écran
        self.unit_var = tk.StringVar()

        # --- Initialisation de l'UI ---
        self._setup_widgets()
        self.load_all_settings()

    def _setup_widgets(self):
        """Crée et assemble les composants de l'interface."""
        self.columnconfigure(0, weight=1)

        # --- Ligne 1: Conteneur pour Langue et Unités ---
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_frame.columnconfigure((0, 1), weight=1)

        # Composant Langue
        self.language_frame = LanguageSettingsFrame(top_frame, on_change_callback=self._on_language_change)
        self.language_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Composant Unités
        self.unit_frame = UnitSettingsFrame(top_frame, on_change_callback=self._on_unit_change)
        self.unit_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # Composant pour l'affichage des onglets
        # On importe le registre pour le rendre disponible ici
        optional_tabs = self.config_manager.get_app_config('OPTIONAL_TABS', [])

        # On crée les callbacks dynamiquement en parcourant le registre
        feature_callbacks = {
            tab_info["id"]: (
                # On utilise une astuce lambda pour capturer la bonne valeur de tab_id
                lambda value, tab_id=tab_info["id"]: 
                self.config_manager.set_show_tab(tab_id, value)
            )
            for tab_info in optional_tabs
        }
        self.features_frame = FeaturesToggleFrame(self, callbacks=feature_callbacks)
        self.features_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Composant pour la configuration de l'écran ---
        self.screen_frame = ScreenConfigFrame(self, unit_var=self.unit_var, on_config_validated_callback=self._on_config_validated)
        self.screen_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

    def _on_language_change(self, lang_code: str):
        """Callback appelé par LanguageSettingsFrame."""
        self.config_manager.set_language(lang_code)
        self.language_manager.set_language(lang_code)
        if hasattr(self.master.master, 'load_language'):
            self.master.master.load_language()

    def _on_unit_change(self, unit_code: str):
        """Callback appelé par UnitSettingsFrame."""
        self.unit_var.set(unit_code) # Met à jour la variable partagée
        self.config_manager.set_distance_unit(unit_code)
        
        # Notifie les autres composants du changement d'unité
        self.screen_frame.update_widget_texts() 
        if hasattr(self.master.master, 'update_stats_display'):
            self.master.master.update_stats_display()

    def _on_config_validated(self):
        """Callback appelé par ScreenConfigFrame après validation."""
        if hasattr(self.master.master, 'update_stats_display'):
            self.master.master.update_stats_display()

    def load_all_settings(self):
        """Charge les paramètres dans tous les composants enfants."""
        # On passe le code de l'unité au composant qui en a besoin
        self.unit_var.set(self.config_manager.get_distance_unit())
        
        # On demande à chaque composant de charger ses propres paramètres
        self.language_frame.set_language_code(self.config_manager.get_language())
        self.unit_frame.set_unit_code(self.config_manager.get_distance_unit())
        self.features_frame.load_settings()
        self.screen_frame.load_settings()

    def update_widget_texts(self):
        """Demande à tous les composants enfants de mettre à jour leurs textes."""
        self.language_frame.update_widget_texts()
        self.unit_frame.update_widget_texts()
        self.features_frame.update_widget_texts()
        self.screen_frame.update_widget_texts()