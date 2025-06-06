# gui/about_tab.py

import tkinter as tk
from tkinter import ttk

# Importe le Service Locator pour accéder aux managers
from utils.service_locator import service_locator
# Importe la version de l'application
from version import __version__


class AboutTab(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # Récupère le language_manager via le Service Locator
        self.language_manager = service_locator.get_service("language_manager")

        # Initialise une StringVar pour le texte 'about_text' pour une mise à jour dynamique
        self.about_text_var = tk.StringVar()
        self.version_label_text_var = tk.StringVar() # Pour la version aussi

        self.setup_widgets()
        # Appel initial pour définir les textes
        self.update_widget_texts()

    def setup_widgets(self):
        # Affiche le texte "À propos" en utilisant la StringVar
        about_label = ttk.Label(self, textvariable=self.about_text_var)
        about_label.pack(padx=10, pady=10)

        # Affiche la version de l'application en utilisant la StringVar
        version_label = ttk.Label(self, textvariable=self.version_label_text_var)
        version_label.pack(padx=10, pady=5)

    def update_widget_texts(self):
        """Met à jour les textes des widgets dans cet onglet suite à un changement de langue."""
        self.about_text_var.set(self.language_manager.get_text('about_text', 'About this application...'))
        self.version_label_text_var.set(f"{self.language_manager.get_text('version_label', 'Version:')} {__version__}")