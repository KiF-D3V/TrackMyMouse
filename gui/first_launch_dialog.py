# gui/first_launch_dialog.py

import tkinter as tk
from tkinter import ttk, messagebox
from utils.service_locator import service_locator
import logging

logger = logging.getLogger(__name__)

class FirstLaunchDialog:
    def __init__(self, parent):
        logger.info("Initialisation de FirstLaunchDialog...")
        self.parent = parent

        self.config_manager = service_locator.get_service("config_manager")
        self.language_manager = service_locator.get_service("language_manager")
        
        self.top = tk.Toplevel(self.parent)
        # self.top.transient(self.parent) # Commenté pour assurer la visibilité
        self.top.resizable(False, False)

        # Variables pour les widgets
        self.language_var = tk.StringVar(self.top)
        self.width_var = tk.StringVar(self.top)
        self.height_var = tk.StringVar(self.top)
        self.unit_var = tk.StringVar(self.top)
        
        # Initialiser les variables avec les préférences actuelles
        self.language_var.set(self.config_manager.get_language())
        self.unit_var.set(self.config_manager.get_distance_unit())

        self.setup_ui() # Configure l'interface utilisateur
        self._update_dialog_texts() # Met à jour les textes avec la langue initiale
        self.update_dimension_labels() # Met à jour les labels de dimension avec l'unité initiale
        
        self.top.update_idletasks() 
        self._center_dialog() # Centre le dialogue à l'écran
        
        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        if hasattr(self, 'width_entry') and self.width_entry: # S'assurer que width_entry est créé
            self.width_entry.focus_set()
        self.top.grab_set() 
        
        is_mapped = self.top.winfo_ismapped()
        is_viewable = self.top.winfo_viewable()
        logger.debug(f"État final du dialogue au lancement - ismapped: {is_mapped}, isviewable: {is_viewable}")
        logger.info("FirstLaunchDialog initialisé, centré et modal.")

    def _center_dialog(self):
        """Calcule les dimensions et centre le dialogue."""
        self.top.update_idletasks() 
        req_width = self.top.winfo_reqwidth()
        req_height = self.top.winfo_reqheight()
        logger.debug(f"Dimensions requises calculées: {req_width}x{req_height}")

        min_width = 380 
        # Augmenter min_height pour accommoder le nouveau cadre de langue
        min_height = 380 # Ajusté par rapport aux 320 précédents
        
        final_width = max(req_width, min_width)
        final_height = max(req_height, min_height)
        
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width // 2) - (final_width // 2)
        y = (screen_height // 2) - (final_height // 2)

        self.top.geometry(f'{final_width}x{final_height}+{x}+{y}')
        logger.debug(f"Géométrie du dialogue définie à: {final_width}x{final_height}+{x}+{y}")
        
        # Assurer que le dialogue est visible
        self.top.deiconify()
        self.top.lift()


    def setup_ui(self):
        """Configure les widgets de l'interface utilisateur du dialogue."""
        # main_frame est déclaré ici pour être accessible par _update_dialog_texts si nécessaire pour le titre
        self.main_frame = ttk.Frame(self.top, padding="15")
        self.main_frame.pack(fill='both', expand=True)

        # Les textes des labels et boutons seront définis dans _update_dialog_texts
        self.welcome_label = ttk.Label(self.main_frame, wraplength=350, justify='center')
        self.welcome_label.pack(pady=10)
        self.prompt_label = ttk.Label(self.main_frame, wraplength=350, justify='left')
        self.prompt_label.pack(pady=5)

        # --- Cadre pour la sélection de la langue ---
        self.language_settings_frame = ttk.LabelFrame(self.main_frame) # Texte sera mis par _update_dialog_texts
        self.language_settings_frame.pack(padx=10, pady=(10,5), fill='x')

        language_names = self.language_manager.get_language_names() # Ex: {'fr': 'Français', 'en': 'English'}
        for lang_code, lang_name in language_names.items():
            rb = ttk.Radiobutton(self.language_settings_frame, text=lang_name, variable=self.language_var, 
                                 value=lang_code, command=self._on_language_changed)
            rb.pack(side='left', padx=5, pady=5)
        # ---------------------------------------------

        self.unit_frame = ttk.LabelFrame(self.main_frame) # Texte sera mis par _update_dialog_texts
        self.unit_frame.pack(padx=10, pady=5, fill='x')
        
        self.metric_rb = ttk.Radiobutton(self.unit_frame, variable=self.unit_var, value='metric', command=self.update_dimension_labels)
        self.metric_rb.pack(side='left', padx=5, pady=5)
        self.imperial_rb = ttk.Radiobutton(self.unit_frame, variable=self.unit_var, value='imperial', command=self.update_dimension_labels)
        self.imperial_rb.pack(side='left', padx=5, pady=5)


        self.dim_frame = ttk.LabelFrame(self.main_frame) # Texte sera mis par _update_dialog_texts
        self.dim_frame.pack(padx=10, pady=5, fill='x')

        self.width_label = ttk.Label(self.dim_frame, text="") # Sera mis par update_dimension_labels
        self.width_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.width_entry = ttk.Entry(self.dim_frame, textvariable=self.width_var, width=15)
        self.width_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.height_label = ttk.Label(self.dim_frame, text="") # Sera mis par update_dimension_labels
        self.height_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.height_entry = ttk.Entry(self.dim_frame, textvariable=self.height_var, width=15)
        self.height_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        self.validate_button = ttk.Button(self.main_frame, command=self.validate_and_save) # Texte sera mis par _update_dialog_texts
        self.validate_button.pack(pady=15)
        logger.debug("Structure UI du dialogue configurée (textes à mettre à jour).")

    def _update_dialog_texts(self):
        """Met à jour tous les textes traduisibles du dialogue."""
        logger.debug(f"Mise à jour des textes du dialogue pour la langue : {self.language_manager.get_current_language()}")
        self.top.title(self.language_manager.get_text('first_launch_dialog_title', 'First Launch Setup'))
        self.welcome_label.config(text=self.language_manager.get_text('welcome_message', 'Welcome to Mouse Tracker!'))
        self.prompt_label.config(text=self.language_manager.get_text('first_launch_prompt', "To accurately track your mouse distance, please provide your screen's physical dimensions."))
        
        self.language_settings_frame.config(text=self.language_manager.get_text('language_settings', 'Language Settings'))
        # Les textes des radiobuttons de langue sont déjà fixés lors de la création.

        self.unit_frame.config(text=self.language_manager.get_text('unit_selection', 'Select Unit System'))
        self.metric_rb.config(text=self.language_manager.get_text('unit_metric_full', 'Metric (cm)'))
        self.imperial_rb.config(text=self.language_manager.get_text('unit_imperial_full', 'Imperial (inches)'))
        
        self.dim_frame.config(text=self.language_manager.get_text('screen_dimensions', 'Screen Dimensions'))
        # Les labels width_label et height_label sont mis à jour par update_dimension_labels

        self.validate_button.config(text=self.language_manager.get_text('validate_button', 'Validate'))
        
        # Mettre à jour les labels de dimension car les textes (cm/inches) peuvent dépendre de la langue
        self.update_dimension_labels()
        logger.debug("Textes du dialogue mis à jour.")

    def _on_language_changed(self):
        """Appelé lorsque la sélection de la langue change."""
        selected_lang_code = self.language_var.get()
        logger.info(f"Langue sélectionnée dans le dialogue: {selected_lang_code}")
        self.language_manager.set_language(selected_lang_code)
        # Mettre à jour les textes du dialogue pour refléter la nouvelle langue
        self._update_dialog_texts()
        # La préférence sera sauvegardée lors de la validation finale.

    def update_dimension_labels(self):
        """Met à jour les labels pour la largeur et la hauteur en fonction de l'unité sélectionnée."""
        unit = self.unit_var.get()
        if unit == 'metric':
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_cm', 'Width (cm):'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_cm', 'Height (cm):'))
        else: # imperial
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_inches', 'Width (inches):'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_inches', 'Height (inches):'))
        logger.debug(f"Labels de dimension mis à jour pour l'unité: {unit}")


    def validate_and_save(self):
        """Valide les entrées et sauvegarde les préférences."""
        logger.debug("Validation et sauvegarde des données du dialogue...")
        
        # Sauvegarde de la langue sélectionnée
        selected_lang_code = self.language_var.get()
        self.config_manager.set_language(selected_lang_code)
        # S'assurer que le language_manager est aussi à jour pour le reste de la session
        self.language_manager.set_language(selected_lang_code) 
        logger.info(f"Langue '{selected_lang_code}' sauvegardée dans les préférences.")

        # Sauvegarde de l'unité sélectionnée (elle est déjà dans self.unit_var)
        selected_unit_code = self.unit_var.get()
        self.config_manager.set_distance_unit(selected_unit_code)
        logger.info(f"Unité '{selected_unit_code}' sauvegardée dans les préférences.")

        try:
            width_str = self.width_var.get()
            height_str = self.height_var.get()

            if not width_str or not height_str: # Vérifier si les champs sont vides
                 messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), 
                                     self.language_manager.get_text('invalid_numeric_input', 'Please enter numeric values for width and height.'), 
                                     parent=self.top)
                 return

            width = float(width_str)
            height = float(height_str)
            
            if width <= 0 or height <= 0:
                messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), 
                                     self.language_manager.get_text('invalid_dimension_message', 'Please enter valid positive dimensions.'), 
                                     parent=self.top)
                return

            self.config_manager.set_physical_dimensions(width, height, selected_unit_code)
            self.config_manager.set_screen_config_verified(True)
            dpi = self.config_manager.calculate_and_set_dpi()
            
            msg = self.language_manager.get_text('config_saved_success', 'Configuration saved successfully.')
            if dpi:
                msg += f" {self.language_manager.get_text('calculated_dpi_label', 'Calculated DPI:')} {dpi:.2f}"
            messagebox.showinfo(self.language_manager.get_text('config_saved_title', 'Configuration Saved'), msg, parent=self.top)
            logger.info("Configuration (dimensions, DPI) sauvegardée avec succès depuis le dialogue.")
            
            self.config_manager.set_show_first_launch_dialog(False)

            self.on_closing(close_app=False) # Ferme le dialogue sans quitter l'app

        except ValueError: # Si float() échoue
            logger.warning("Erreur de valeur (non numérique) lors de la validation du dialogue.", exc_info=True)
            messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), 
                                 self.language_manager.get_text('invalid_numeric_input', 'Please enter numeric values for width and height.'), 
                                 parent=self.top)
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la validation: {e}", exc_info=True)
            messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), 
                                 f"{self.language_manager.get_text('an_error_occurred', 'An error occurred')}: {e}", 
                                 parent=self.top)


    def on_closing(self, close_app=True):
        """Gère la fermeture du dialogue."""
        logger.debug(f"Tentative de fermeture du dialogue. close_app={close_app}, screen_config_verified={self.config_manager.get_screen_config_verified()}")
        
        # Si l'écran n'a pas été configuré ET que la fermeture implique de quitter l'app (bouton X)
        if not self.config_manager.get_screen_config_verified() and close_app:
            title = self.language_manager.get_text('exit_app_title', 'Exit Application')
            prompt = self.language_manager.get_text('exit_app_prompt', 'Screen dimensions are crucial for accurate tracking. Do you want to exit the application?')
            if messagebox.askyesno(title, prompt, parent=self.top):
                logger.warning("L'utilisateur a choisi de quitter l'application car la configuration initiale n'a pas été validée.")
                if self.parent: 
                    self.parent.destroy() # Ferme l'application principale
            else:
                logger.info("L'utilisateur a choisi de ne pas quitter, le dialogue reste ouvert.")
                return # Empêche la fermeture du dialogue
        
        logger.info("Fermeture du dialogue FirstLaunch.")
        self.top.destroy()