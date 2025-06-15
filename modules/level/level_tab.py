# modules/level/level_tab.py

import tkinter as tk
from tkinter import ttk
from utils.service_locator import service_locator

class LevelTab(ttk.Frame):
    """
    Onglet de l'interface graphique affichant les informations de niveau et d'XP.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Récupération des managers via le service locator
        self.language_manager = service_locator.get_service("language_manager")
        self.xp_manager = service_locator.get_service("xp_manager")
        self.event_manager = service_locator.get_service("event_manager")

        # S'abonner à l'événement de level up pour des mises à jour spéciales
        self.event_manager.subscribe("level_up", self._on_level_up)

        self.columnconfigure(0, weight=1)

        # Création des widgets de l'onglet
        self._create_widgets()
        
    def _create_widgets(self):
        """Crée et positionne tous les widgets de l'onglet selon la disposition finale."""
        # --- Configuration de la grille pour centrer le contenu verticalement ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Variables de contrôle pour les labels ---
        self.level_var = tk.StringVar(value="...")
        self.xp_var = tk.StringVar(value="... / ... XP")

        # --- Création des widgets ---
        
        # Label pour le CHIFFRE du niveau (grande police, en gras)
        level_number_label = ttk.Label(self, textvariable=self.level_var, font=("Segoe UI", 48, "bold"), anchor="center")
        level_number_label.grid(row=1, column=0, sticky="ew")

        # Barre de progression
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=2, column=0, padx=50, pady=15, sticky="ew")

        # Label pour le texte d'XP
        xp_text_label = ttk.Label(self, textvariable=self.xp_var, anchor="center")
        xp_text_label.grid(row=3, column=0, sticky="ew")

    def update_display(self):
        """
        Met à jour les widgets de l'onglet avec les dernières données de XPManager.
        """
        if not self.xp_manager:
            return

        details = self.xp_manager.get_level_details()
        if not details:
            return

        # --- MODIFIÉ : On n'affiche que le chiffre pour le niveau ---
        self.level_var.set(str(details['current_level']))
        
        self.xp_var.set(details['current_xp_str'])
        
        self.progress_bar['value'] = details['progress_percentage']
        
    def _on_level_up(self, new_level: int):
        """
        Callback pour l'événement 'level_up'.
        """
        # À FAIRE : Gérer l'affichage d'une notification de level up
        print(f"LevelTab a reçu l'événement level_up ! Nouveau niveau : {new_level}")
        self.update_display()

    def on_language_change(self):
        """
        Méthode pour mettre à jour les textes lors d'un changement de langue.
        """
        # La méthode update_display récupère déjà le texte traduit, il suffit de l'appeler.
        self.update_display()