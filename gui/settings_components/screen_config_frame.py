# gui/settings_components/screen_config_frame.py

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
import logging

from utils.service_locator import service_locator

logger = logging.getLogger(__name__)

class ScreenConfigFrame(ttk.LabelFrame):
    """
    Composant d'interface dédié à la configuration physique de l'écran.
    """
    def __init__(self, master, unit_var: tk.StringVar, on_config_validated_callback: Callable[[], None]):
        """
        Initialise le cadre de configuration de l'écran.

        Args:
            master: Le widget parent.
            unit_var: La StringVar partagée qui contient l'unité actuelle ('metric' ou 'imperial').
            on_config_validated_callback: La fonction à appeler après une validation réussie.
        """
        super().__init__(master)
        
        self.unit_var = unit_var
        self.on_config_validated_callback = on_config_validated_callback

        # --- Dépendances ---
        self.config_manager = service_locator.get_service("config_manager")
        self.language_manager = service_locator.get_service("language_manager")
        
        # --- Initialisation de l'UI ---
        self._setup_widgets()
        self.load_settings()
        self.update_widget_texts()
        logger.info("ScreenConfigFrame initialisé.")

    def _setup_widgets(self):
        """Crée et positionne les widgets à l'intérieur de ce cadre."""
        # Un cadre interne pour utiliser grid plus facilement
        grid_container = ttk.Frame(self)
        grid_container.pack(pady=5, padx=5)

        # Largeur
        self.width_label = ttk.Label(grid_container, text="")
        self.width_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.width_entry = ttk.Entry(grid_container, width=10)
        self.width_entry.grid(row=0, column=1, padx=5, pady=5)

        # Hauteur
        self.height_label = ttk.Label(grid_container, text="")
        self.height_label.grid(row=0, column=2, padx=(10, 5), pady=5, sticky="w")
        self.height_entry = ttk.Entry(grid_container, width=10)
        self.height_entry.grid(row=0, column=3, padx=5, pady=5)

        # Bouton de validation
        self.validate_button = ttk.Button(grid_container, text="", command=self._on_validate_click)
        self.validate_button.grid(row=0, column=4, padx=(15, 5), pady=5)

    def _on_validate_click(self):
        """Logique exécutée lors du clic sur le bouton 'Valider'."""
        logger.debug("Clic sur le bouton de validation de la configuration de l'écran.")
        width_str = self.width_entry.get()
        height_str = self.height_entry.get()
        unit_code = self.unit_var.get()

        try:
            width = float(width_str)
            height = float(height_str)
            if width > 0 and height > 0:
                self.config_manager.set_physical_dimensions(width, height, unit_code)
                self.config_manager.set_screen_config_verified(True)
                dpi = self.config_manager.calculate_and_set_dpi()
                
                message = self.language_manager.get_text('screen_config_saved_message')
                if dpi:
                    message += f" {self.language_manager.get_text('calculated_dpi_label')} {dpi:.2f}"
                messagebox.showinfo(self.language_manager.get_text('config_saved_title'), message)
                
                # Notification au parent que la configuration a changé
                self.on_config_validated_callback()
            else:
                messagebox.showerror(self.language_manager.get_text('error_title'), self.language_manager.get_text('invalid_dimension_message'))
        except ValueError:
            messagebox.showerror(self.language_manager.get_text('error_title'), self.language_manager.get_text('invalid_input_message'))

    def load_settings(self):
        """Charge les valeurs depuis le PreferenceManager dans les champs de saisie."""
        logger.debug("Chargement des paramètres de l'écran.")
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(self.config_manager.get_physical_width_cm()) or "")
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(self.config_manager.get_physical_height_cm()) or "")

    def update_widget_texts(self):
        """Met à jour tous les textes de ce composant."""
        logger.debug("Mise à jour des textes pour ScreenConfigFrame.")
        self.config(text=self.language_manager.get_text('screen_config'))
        self.validate_button.config(text=self.language_manager.get_text('validate_screen_config_button'))
        
        # Met à jour les labels cm/pouces
        unit_code = self.unit_var.get()
        if unit_code == 'metric':
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_cm'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_cm'))
        elif unit_code == 'imperial':
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_inches'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_inches'))