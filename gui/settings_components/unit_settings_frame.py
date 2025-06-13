# gui/settings_components/unit_settings_frame.py

import tkinter as tk
from tkinter import ttk
from typing import Callable

from utils.service_locator import service_locator

class UnitSettingsFrame(ttk.LabelFrame):
    """
    Composant d'interface dédié à la sélection de l'unité de distance.
    Il est autonome et notifie son parent d'un changement via un callback.
    """
    def __init__(self, master, on_change_callback: Callable[[str], None]):
        """
        Initialise le cadre des paramètres d'unité.

        Args:
            master: Le widget parent.
            on_change_callback: La fonction à appeler lorsque l'unité change.
                                Elle recevra le nouveau code d'unité (ex: 'metric') en argument.
        """
        super().__init__(master)
        
        self.on_change_callback = on_change_callback

        # --- Dépendances ---
        self.language_manager = service_locator.get_service("language_manager")
        
        # --- Variables et état interne ---
        self.unit_var = tk.StringVar() # Stocke le code d'unité interne (ex: 'metric')
        self.unit_codes = ['metric', 'imperial']
        self.unit_display_to_code = {}
        self.unit_code_to_display = {}

        # --- Initialisation de l'UI ---
        self._setup_widgets()
        self.update_widget_texts() # Définit les textes et les valeurs initiales

    def _setup_widgets(self):
        """Crée et positionne les widgets à l'intérieur de ce cadre."""
        self.columnconfigure(1, weight=1) # Permet au combobox de s'étirer

        # Label "Unités :"
        self.label = ttk.Label(self, text="")
        self.label.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="w")

        # Menu déroulant des unités
        self.combobox = ttk.Combobox(self, state='readonly', width=12)
        self.combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combobox.bind("<<ComboboxSelected>>", self._on_selection_change)

    def _on_selection_change(self, event=None):
        """
        Gère l'événement de sélection d'une nouvelle unité dans le combobox.
        Met à jour l'état interne et appelle le callback parent.
        """
        selected_display_text = self.combobox.get()
        selected_code = self.unit_display_to_code.get(selected_display_text)
        
        if selected_code and selected_code != self.unit_var.get():
            self.unit_var.set(selected_code)
            # Notifie le parent (SettingsTab) que l'unité a changé
            self.on_change_callback(selected_code)

    def update_widget_texts(self):
        """
        Met à jour tous les textes de ce composant.
        Cette méthode est destinée à être appelée par le parent (SettingsTab).
        """
        # 1. MODIFIÉ : On récupère les dictionnaires directement depuis le LanguageManager
        self.unit_display_to_code, self.unit_code_to_display = self.language_manager.get_unit_mappings()

        # 2. Mettre à jour les textes des widgets
        self.config(text=self.language_manager.get_text('unit_settings'))
        self.label.config(text=self.language_manager.get_text('unit_label'))
        
        # 3. Mettre à jour les valeurs et la sélection du combobox
        self.combobox.config(values=list(self.unit_display_to_code.keys()))
        
        current_unit_code = self.unit_var.get()
        display_text = self.unit_code_to_display.get(current_unit_code)
        if display_text:
            self.combobox.set(display_text)
            
    def set_unit_code(self, unit_code: str):
        """
        Permet au parent de définir l'unité de ce composant de manière programmatique.
        """
        self.unit_var.set(unit_code)
        self.update_widget_texts()