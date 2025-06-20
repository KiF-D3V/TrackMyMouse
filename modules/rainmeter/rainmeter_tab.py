# modules/rainmeter/rainmeter_tab.py

import tkinter as tk
from tkinter import ttk

from core.service_locator import service_locator

class RainmeterTab(ttk.Frame):
    """
    Onglet de l'interface dédié à la fonctionnalité d'export pour Rainmeter.
    Sert de placeholder pour le moment.
    """
    def __init__(self, master=None):
        super().__init__(master)
        
        self.language_manager = service_locator.get_service("language_manager")
        
        # --- Initialisation de l'UI ---
        self._setup_widgets()
        self.update_widget_texts()

    def _setup_widgets(self):
        """Crée les widgets du placeholder."""
        # Un label centré pour le message
        self.placeholder_label = ttk.Label(self, anchor="center")
        self.placeholder_label.pack(expand=True, fill="both", padx=20, pady=20)

    def update_widget_texts(self):
        """Met à jour les textes de l'onglet."""
        # Nous aurons besoin d'une nouvelle clé de langue
        coming_soon_text = self.language_manager.get_text(
            'rainmeter_coming_soon', 
            "Rainmeter export feature coming soon..."
        )
        self.placeholder_label.config(text=coming_soon_text)