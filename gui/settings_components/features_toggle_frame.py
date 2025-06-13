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

        Args:
            master: Le widget parent.
            callbacks: Un dictionnaire de fonctions à appeler lorsqu'une case est cochée.
                       Ex: {'history': on_history_toggle, 'records': on_records_toggle}
        """
        super().__init__(master)
        
        self.callbacks = callbacks

        # --- Dépendances ---
        self.language_manager = service_locator.get_service("language_manager")
        self.preference_manager = service_locator.get_service("preference_manager")

        # --- Variables d'état ---
        self.vars = {
            'history': tk.BooleanVar(),
            'records': tk.BooleanVar(),
            'rainmeter': tk.BooleanVar()
        }
        
        # --- Initialisation de l'UI ---
        self._setup_widgets()
        self.load_settings()
        self.update_widget_texts()

    def _setup_widgets(self):
        """Crée et positionne les widgets."""
        self.columnconfigure(0, weight=1)

        # Création des labels et des cases à cocher en boucle
        self.labels = {}
        checkboxes = {}
        
        feature_keys = ['history', 'records', 'rainmeter']
        for i, key in enumerate(feature_keys):
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
        self.notice_label.grid(row=len(feature_keys), column=0, columnspan=2, padx=5, pady=(10, 5), sticky="w")
        ttk.Style(self).configure("Italic.TLabel", font=("Segoe UI", 9, "italic"))

    def _on_toggle(self, feature_key: str):
        """Callback générique appelé lorsqu'une case est cochée."""
        if feature_key in self.callbacks:
            new_value = self.vars[feature_key].get()
            callback_func = self.callbacks[feature_key]
            callback_func(new_value)

    def load_settings(self):
        """Charge l'état initial des cases à cocher depuis les préférences."""
        self.vars['history'].set(self.preference_manager.get_show_history_tab())
        self.vars['records'].set(self.preference_manager.get_show_records_tab())
        self.vars['rainmeter'].set(self.preference_manager.get_show_rainmeter_tab())

    def update_widget_texts(self):
        """Met à jour tous les textes de ce composant."""
        self.config(text=self.language_manager.get_text('features_settings_title'))
        
        self.labels['history'].config(text=self.language_manager.get_text('show_history_tab_label'))
        self.labels['records'].config(text=self.language_manager.get_text('show_records_tab_label'))
        self.labels['rainmeter'].config(text=self.language_manager.get_text('show_rainmeter_tab_label'))
        
        self.notice_label.config(text=self.language_manager.get_text('features_restart_required_notice'))