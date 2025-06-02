# gui/settings_tab.py

import tkinter as tk
from tkinter import ttk, messagebox

from utils.service_locator import service_locator

class SettingsTab(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.language_manager = service_locator.get_service("language_manager")
        self.stats_manager = service_locator.get_service("stats_manager")
        self.preference_manager = service_locator.get_service("preference_manager")

        self.width_label = None
        self.height_label = None
        self.width_entry = None
        self.height_entry = None
        self.unit_var = tk.StringVar(self)
        self.language_var = tk.StringVar(self)

        # Définition des options pour les combobox (VALEURS INTERNES/CODES)
        self.language_codes = ['fr', 'en'] # Renommé pour clarté
        self.unit_codes = ['metric', 'imperial'] # Renommé pour clarté

        # --- NOUVEAU : Crée des dictionnaires de mapping pour les Combobox ---
        # language_display_to_code: {'Français': 'fr', 'English': 'en'}
        self.language_display_to_code = {self.language_manager.get_text(f'language_{code}', code): code for code in self.language_codes}
        # unit_display_to_code: {'Métrique': 'metric', 'Impérial': 'imperial'}
        self.unit_display_to_code = {self.language_manager.get_text(f'unit_{code}', code): code for code in self.unit_codes}
        
        # Et des dictionnaires pour l'inverse : code_to_display_value
        self.language_code_to_display = {code: self.language_manager.get_text(f'language_{code}', code) for code in self.language_codes}
        self.unit_code_to_display = {code: self.language_manager.get_text(f'unit_{code}', code) for code in self.unit_codes}


        # S'assurer qu'une valeur par défaut est définie pour language_var et unit_var via PreferenceManager
        initial_lang_code = self.preference_manager.get_language()
        if initial_lang_code not in self.language_codes:
            initial_lang_code = 'en' # Défaut si non valide
        # La StringVar stocke le CODE (ex: 'fr'), mais le Combobox affichera le texte traduit
        self.language_var.set(initial_lang_code)

        initial_unit_code = self.preference_manager.get_distance_unit()
        if initial_unit_code not in self.unit_codes:
            initial_unit_code = 'metric' # Défaut si non valide
        # La StringVar stocke le CODE (ex: 'metric'), mais le Combobox affichera le texte traduit
        self.unit_var.set(initial_unit_code)
        
        self.setup_widgets()
        
        # La trace est définie après s'être assuré d'une valeur initiale valide
        self.unit_var.trace_add("write", self.update_screen_dimension_labels)

        self.load_settings() # Charge les paramètres initiaux et met à jour l'affichage
        self.update_screen_dimension_labels() # Initialise les labels des dimensions de l'écran


    def setup_widgets(self):
        # Frame pour la langue
        self.language_frame = ttk.LabelFrame(self, text=self.language_manager.get_text('language_settings', 'Language Settings'))
        self.language_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(self.language_frame, text=self.language_manager.get_text('language_label', 'Language:')).pack(side='left', padx=5)
        
        # Les valeurs du Combobox sont les textes traduits (Français, English)
        self.language_menu = ttk.Combobox(self.language_frame, textvariable=self.language_var, 
                                            values=list(self.language_display_to_code.keys()), # Utilise les clés (textes affichés)
                                            state='readonly')
        self.language_menu.pack(side='left', padx=5)
        self.language_menu.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Frame pour les unités de distance
        self.unit_frame = ttk.LabelFrame(self, text=self.language_manager.get_text('unit_settings', 'Distance Units'))
        self.unit_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(self.unit_frame, text=self.language_manager.get_text('unit_label', 'Units:')).pack(side='left', padx=5)
        
        # Les valeurs du Combobox sont les textes traduits (Métrique, Impérial)
        self.unit_menu = ttk.Combobox(self.unit_frame, textvariable=self.unit_var, 
                                        values=list(self.unit_display_to_code.keys()), # Utilise les clés (textes affichés)
                                        state='readonly')
        self.unit_menu.pack(side='left', padx=5)
        self.unit_menu.bind("<<ComboboxSelected>>", self.on_unit_change)
        
        # Frame pour la configuration de l'écran
        self.screen_config_frame = ttk.LabelFrame(self, text=self.language_manager.get_text('screen_config', 'Screen Configuration (Physical)'))
        self.screen_config_frame.pack(padx=10, pady=10, fill='x')

        self.width_label = ttk.Label(self.screen_config_frame, text="")
        self.width_label.pack(side='left', padx=5)
        self.width_entry = ttk.Entry(self.screen_config_frame, width=10)
        self.width_entry.pack(side='left', padx=5)
        self.width_entry.insert(0, str(self.preference_manager.get_physical_width_cm()) if self.preference_manager.get_physical_width_cm() else "")

        self.height_label = ttk.Label(self.screen_config_frame, text="")
        self.height_label.pack(side='left', padx=5)
        self.height_entry = ttk.Entry(self.screen_config_frame, width=10)
        self.height_entry.pack(side='left', padx=5)
        self.height_entry.insert(0, str(self.preference_manager.get_physical_height_cm()) if self.preference_manager.get_physical_height_cm() else "")

        self.validate_button = ttk.Button(self.screen_config_frame, text=self.language_manager.get_text('validate_screen_config_button', 'Validate Configuration'), command=self.validate_screen_config)
        self.validate_button.pack(pady=10)


    def load_settings(self):
        # Met à jour la valeur de la variable language_var depuis PreferenceManager
        current_lang_code = self.preference_manager.get_language()
        # Assure que la variable language_var contient le CODE (ex: 'fr')
        self.language_var.set(current_lang_code if current_lang_code in self.language_codes else 'en')
        # Met à jour le texte AFFICHÉ dans le Combobox, en utilisant le mapping
        self.language_menu.set(self.language_code_to_display.get(self.language_var.get(), self.language_var.get()))

        # Met à jour la valeur de la variable unit_var depuis PreferenceManager
        current_unit_code = self.preference_manager.get_distance_unit()
        # Assure que la variable unit_var contient le CODE (ex: 'metric')
        self.unit_var.set(current_unit_code if current_unit_code in self.unit_codes else 'metric')
        # Met à jour le texte AFFICHÉ dans le Combobox, en utilisant le mapping
        self.unit_menu.set(self.unit_code_to_display.get(self.unit_var.get(), self.unit_var.get()))

        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(self.preference_manager.get_physical_width_cm()) if self.preference_manager.get_physical_width_cm() else "")
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(self.preference_manager.get_physical_height_cm()) if self.preference_manager.get_physical_height_cm() else "")


    def update_screen_dimension_labels(self, *args):
        unit = self.unit_var.get() # Ceci contient le CODE ('metric' ou 'imperial')
        if unit == 'metric':
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_cm', 'Width (cm):'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_cm', 'Height (cm):'))
        elif unit == 'imperial':
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_inches', 'Width (inches):'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_inches', 'Height (inches):'))

    def on_language_change(self, event):
        # La textvariable self.language_var contient déjà le texte affiché du combobox (ex: "Français")
        selected_language_display = self.language_var.get()
        # Utilise le dictionnaire de mapping pour obtenir le code interne
        selected_language_code = self.language_display_to_code.get(selected_language_display, 'en') # Fallback to 'en'

        self.preference_manager.set_language(selected_language_code)
        
        # Important : Mettre à jour le language_manager avec le CODE correct, pas le texte affiché
        self.language_manager.set_language(selected_language_code) 
        
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'load_language'):
            self.master.master.load_language()
        
        self.update_widget_texts()


    def on_unit_change(self, event):
        # La textvariable self.unit_var contient déjà le texte affiché du combobox (ex: "Métrique")
        selected_unit_display = self.unit_var.get()
        # Utilise le dictionnaire de mapping pour obtenir le code interne
        selected_unit_code = self.unit_display_to_code.get(selected_unit_display, 'metric') # Fallback to 'metric'
        
        self.preference_manager.set_distance_unit(selected_unit_code)

        if hasattr(self.master, 'master') and hasattr(self.master.master, 'update_stats_display'):
            self.master.master.update_stats_display()
        
        self.update_screen_dimension_labels()


    def validate_screen_config(self):
        width_str = self.width_entry.get()
        height_str = self.height_entry.get()
        # La textvariable unit_var contient déjà le CODE ('metric' ou 'imperial')
        unit = self.unit_var.get() 

        try:
            width = float(width_str)
            height = float(height_str)
            if width > 0 and height > 0:
                self.preference_manager.set_physical_dimensions(width, height, unit)
                self.preference_manager.set_screen_config_verified(True)
                dpi = self.preference_manager.calculate_and_set_dpi()
                
                message = self.language_manager.get_text('screen_config_saved_message', 'Screen configuration has been saved.')
                if dpi:
                    message += f" {self.language_manager.get_text('calculated_dpi_label', 'Calculated DPI:')} {dpi:.2f}"
                messagebox.showinfo(self.language_manager.get_text('config_saved_title', 'Configuration Saved'), message)
                
                if hasattr(self.master, 'master') and hasattr(self.master.master, 'update_stats_display'):
                    self.master.master.update_stats_display()
            else:
                messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), self.language_manager.get_text('invalid_dimension_message', 'Please enter valid positive dimensions.'))
        except ValueError:
            messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), self.language_manager.get_text('invalid_input_message', 'Please enter numeric values for width and height.'))


    def update_widget_texts(self):
        """Met à jour le texte de tous les widgets de cet onglet après un changement de langue."""
        # Recrée les mappings car la langue a changé
        self.language_display_to_code = {self.language_manager.get_text(f'language_{code}', code): code for code in self.language_codes}
        self.unit_display_to_code = {self.language_manager.get_text(f'unit_{code}', code): code for code in self.unit_codes}
        self.language_code_to_display = {code: self.language_manager.get_text(f'language_{code}', code) for code in self.language_codes}
        self.unit_code_to_display = {code: self.language_manager.get_text(f'unit_{code}', code) for code in self.unit_codes}


        # Mise à jour des titres des LabelFrames
        self.language_frame.config(text=self.language_manager.get_text('language_settings', 'Language Settings'))
        self.unit_frame.config(text=self.language_manager.get_text('unit_settings', 'Distance Units'))
        self.screen_config_frame.config(text=self.language_manager.get_text('screen_config', 'Screen Configuration (Physical)'))

        # Mise à jour des labels (Language:, Units:)
        self.language_frame.winfo_children()[0].config(text=self.language_manager.get_text('language_label', 'Language:'))
        self.unit_frame.winfo_children()[0].config(text=self.language_manager.get_text('unit_label', 'Units:'))
        
        # Mise à jour des 'values' des Combobox pour qu'ils affichent les textes traduits
        self.language_menu.config(values=list(self.language_display_to_code.keys()))
        self.unit_menu.config(values=list(self.unit_display_to_code.keys()))

        # Mise à jour de la valeur AFFICHÉE pour les Combobox (en s'assurant que la variable a une valeur valide)
        current_lang_code = self.language_var.get() # C'est le CODE interne
        self.language_menu.set(self.language_code_to_display.get(current_lang_code, current_lang_code))

        current_unit_code = self.unit_var.get() # C'est le CODE interne
        self.unit_menu.set(self.unit_code_to_display.get(current_unit_code, current_unit_code))

        # Mise à jour des labels de largeur/hauteur
        self.update_screen_dimension_labels()

        # Mise à jour du texte du bouton de validation
        self.validate_button.config(text=self.language_manager.get_text('validate_screen_config_button', 'Validate Configuration'))