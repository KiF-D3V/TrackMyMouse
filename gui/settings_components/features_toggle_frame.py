# gui/settings_components/features_toggle_frame.py

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict
from utils.service_locator import service_locator

class FeaturesToggleFrame(ttk.LabelFrame):
    """
    Composant d'interface pour gérer l'activation/désactivation des onglets optionnels.
    """
    def __init__(self, master, callbacks: Dict[str, Callable[[bool], None]]):
        """
        Initialise le cadre des fonctionnalités.
        """
        super().__init__(master)
        
        self.callbacks = callbacks

        # --- Dépendances ---
        self.language_manager = service_locator.get_service("language_manager")
        self.preference_manager = service_locator.get_service("preference_manager")
        
        # --- AJOUT: Import du registre ---
        from config.app_config import OPTIONAL_TABS
        self.optional_tabs = OPTIONAL_TABS

        # --- MODIFIÉ : Création dynamique des variables ---
        self.vars = {tab_info["id"]: tk.BooleanVar() for tab_info in self.optional_tabs}
        
        # --- Initialisation de l'UI ---
        self._setup_widgets()
        self.load_settings()
        self.update_widget_texts()

    def _setup_widgets(self):
        """Crée et positionne les widgets dynamiquement."""
        self.columnconfigure(0, weight=1)

        self.labels = {}
        checkboxes = {}
        
        # --- MODIFIÉ : Boucle sur le registre OPTIONAL_TABS ---
        for i, tab_info in enumerate(self.optional_tabs):
            key = tab_info["id"]
            
            self.labels[key] = ttk.Label(self, text="")
            self.labels[key].grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            checkboxes[key] = ttk.Checkbutton(
                self, 
                variable=self.vars[key], 
                command=lambda k=key: self._on_toggle(k)
            )
            checkboxes[key].grid(row=i, column=1, padx=5, pady=2, sticky="e")

        # Notice de redémarrage
        self.notice_label = ttk.Label(self, text="", style="Italic.TLabel")
        self.notice_label.grid(row=len(self.optional_tabs), column=0, columnspan=2, padx=5, pady=(10, 5), sticky="w")
        ttk.Style(self).configure("Italic.TLabel", font=("Segoe UI", 9, "italic"))

    def _on_toggle(self, feature_key: str):
        """Callback générique appelé lorsqu'une case est cochée."""
        if feature_key in self.callbacks:
            new_value = self.vars[feature_key].get()
            callback_func = self.callbacks[feature_key]
            callback_func(new_value)

    def load_settings(self):
        """Charge l'état initial des cases à cocher dynamiquement."""
        for tab_info in self.optional_tabs:
            key = tab_info["id"]
            # On utilise la méthode générique du PreferenceManager
            is_enabled = self.preference_manager.get_show_tab(key)
            self.vars[key].set(is_enabled)

    def update_widget_texts(self):
        """Met à jour tous les textes de ce composant dynamiquement."""
        self.config(text=self.language_manager.get_text('features_settings_title'))
        
        # --- MODIFIÉ : Boucle sur le registre pour mettre à jour les labels ---
        for tab_info in self.optional_tabs:
            key = tab_info["id"]
            label_key = tab_info["toggle_label_key"]
            if key in self.labels:
                self.labels[key].config(text=self.language_manager.get_text(label_key))
        
        self.notice_label.config(text=self.language_manager.get_text('features_restart_required_notice'))