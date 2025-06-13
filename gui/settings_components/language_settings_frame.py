# gui/settings_components/language_settings_frame.py

import tkinter as tk
from tkinter import ttk
from typing import Callable

from utils.service_locator import service_locator

class LanguageSettingsFrame(ttk.LabelFrame):
    """
    Composant d'interface dédié à la sélection de la langue.
    Il est autonome et notifie son parent d'un changement via un callback.
    """
    def __init__(self, master, on_change_callback: Callable[[str], None]):
        """
        Initialise le cadre des paramètres de langue.

        Args:
            master: Le widget parent.
            on_change_callback: La fonction à appeler lorsque la langue change.
                                Elle recevra le nouveau code de langue (ex: 'fr') en argument.
        """
        super().__init__(master)
        
        self.on_change_callback = on_change_callback

        # --- Dépendances ---
        self.language_manager = service_locator.get_service("language_manager")
        
        # --- Variables et état interne ---
        self.language_var = tk.StringVar() # Stocke le code de langue interne (ex: 'fr')
        self.language_codes = ['fr', 'en']
        self.language_display_to_code = {}
        self.language_code_to_display = {}

        # --- Initialisation de l'UI ---
        self._setup_widgets()
        self.update_widget_texts() # Définit les textes et les valeurs initiales

    def _setup_widgets(self):
        """Crée et positionne les widgets à l'intérieur de ce cadre."""
        self.columnconfigure(1, weight=1) # Permet au combobox de s'étirer

        # Label "Langue :"
        self.label = ttk.Label(self, text="")
        self.label.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="w")

        # Menu déroulant des langues
        self.combobox = ttk.Combobox(self, state='readonly', width=12)
        self.combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combobox.bind("<<ComboboxSelected>>", self._on_selection_change)

    def _on_selection_change(self, event=None):
        """
        Gère l'événement de sélection d'une nouvelle langue dans le combobox.
        Met à jour l'état interne et appelle le callback parent.
        """
        selected_display_text = self.combobox.get()
        selected_code = self.language_display_to_code.get(selected_display_text)
        
        if selected_code and selected_code != self.language_var.get():
            self.language_var.set(selected_code)
            # Notifie le parent (SettingsTab) que la langue a changé
            self.on_change_callback(selected_code)

    def update_widget_texts(self):
        """
        Met à jour tous les textes de ce composant.
        Cette méthode est destinée à être appelée par le parent (SettingsTab)
        lors d'un changement de langue global.
        """
        # 1. MODIFIÉ : On récupère les dictionnaires directement depuis le LanguageManager
        self.language_display_to_code, self.language_code_to_display = self.language_manager.get_language_mappings()

        # 2. Mettre à jour les textes des widgets
        self.config(text=self.language_manager.get_text('language_settings'))
        self.label.config(text=self.language_manager.get_text('language_label'))
        
        # 3. Mettre à jour les valeurs et la sélection du combobox
        self.combobox.config(values=list(self.language_display_to_code.keys()))
        
        current_lang_code = self.language_var.get()
        display_text = self.language_code_to_display.get(current_lang_code)
        if display_text:
            self.combobox.set(display_text)
            
    def set_language_code(self, lang_code: str):
        """
        Permet au parent de définir la langue de ce composant de manière programmatique.
        """
        self.language_var.set(lang_code)
        self.update_widget_texts()