# gui/first_launch_dialog.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class FirstLaunchDialog:
    def __init__(self, parent, language_manager, preference_manager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initialisation de FirstLaunchDialog...")
        self.parent = parent
        self.language_manager = language_manager
        self.preference_manager = preference_manager

        self.top = tk.Toplevel(self.parent)
        self.logger.debug(f"Toplevel créé avec parent: {self.parent}")
        # self.top.transient(self.parent) 
        self.top.resizable(False, False)

        self.width_var = tk.StringVar(self.top)
        self.height_var = tk.StringVar(self.top)
        self.unit_var = tk.StringVar(self.top)
        self.unit_var.set('metric')

        self.setup_ui()
        
        self.top.update_idletasks() 
        req_width = self.top.winfo_reqwidth()
        req_height = self.top.winfo_reqheight()
        self.logger.debug(f"Dimensions requises calculées: {req_width}x{req_height}")

        min_width = 380
        min_height = 320
        final_width = max(req_width, min_width)
        final_height = max(req_height, min_height)
        
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = (screen_width // 2) - (final_width // 2)
        y = (screen_height // 2) - (final_height // 2)

        self.top.geometry(f'{final_width}x{final_height}+{x}+{y}')
        self.logger.debug(f"Géométrie du dialogue définie à: {final_width}x{final_height}+{x}+{y}")
        
        self.top.deiconify()
        self.logger.debug("Dialogue 'deiconified'.")
        self.top.lift()
        self.logger.debug("Dialogue 'lifted'.")
        
        self.update_dimension_labels()
        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.width_entry.focus_set()
        self.top.grab_set() 
        
        # --- NOUVEAUX LOGS DE DIAGNOSTIC ---
        is_mapped = self.top.winfo_ismapped()
        is_viewable = self.top.winfo_viewable()
        self.logger.debug(f"État final du dialogue - ismapped: {is_mapped}, isviewable: {is_viewable}")
        # ------------------------------------
        
        self.logger.info("FirstLaunchDialog initialisé, centré et modal.")

    # ... (le reste de la classe reste inchangé : setup_ui, update_dimension_labels, validate_and_save, on_closing) ...
    # COPIEZ LE RESTE DES MÉTHODES DE LA VERSION PRÉCÉDENTE ICI
    def setup_ui(self):
        self.top.title(self.language_manager.get_text('first_launch_dialog_title', 'First Launch Setup'))
        main_frame = ttk.Frame(self.top, padding="15")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text=self.language_manager.get_text('welcome_message', 'Welcome to Mouse Tracker!'), wraplength=350, justify='center').pack(pady=10)
        ttk.Label(main_frame, text=self.language_manager.get_text('first_launch_prompt', 'To accurately track your mouse distance, please provide your screen\'s physical dimensions.'), wraplength=350, justify='left').pack(pady=5)

        unit_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_text('unit_selection', 'Select Unit System'))
        unit_frame.pack(padx=10, pady=5, fill='x')
        ttk.Radiobutton(unit_frame, text=self.language_manager.get_text('unit_metric_full', 'Metric (cm)'), variable=self.unit_var, value='metric', command=self.update_dimension_labels).pack(side='left', padx=5, pady=5)
        ttk.Radiobutton(unit_frame, text=self.language_manager.get_text('unit_imperial_full', 'Imperial (inches)'), variable=self.unit_var, value='imperial', command=self.update_dimension_labels).pack(side='left', padx=5, pady=5)

        dim_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_text('screen_dimensions', 'Screen Dimensions'))
        dim_frame.pack(padx=10, pady=5, fill='x')

        self.width_label = ttk.Label(dim_frame, text="")
        self.width_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.width_entry = ttk.Entry(dim_frame, textvariable=self.width_var, width=15)
        self.width_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.height_label = ttk.Label(dim_frame, text="")
        self.height_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.height_entry = ttk.Entry(dim_frame, textvariable=self.height_var, width=15)
        self.height_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        validate_button = ttk.Button(main_frame, text=self.language_manager.get_text('validate_button', 'Validate'), command=self.validate_and_save)
        validate_button.pack(pady=15)
        self.logger.debug("UI du dialogue configurée.")


    def update_dimension_labels(self):
        unit = self.unit_var.get()
        if unit == 'metric':
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_cm', 'Width (cm):'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_cm', 'Height (cm):'))
        else: # imperial
            self.width_label.config(text=self.language_manager.get_text('physical_width_label_inches', 'Width (inches):'))
            self.height_label.config(text=self.language_manager.get_text('physical_height_label_inches', 'Height (inches):'))

    def validate_and_save(self):
        self.logger.debug("Validation et sauvegarde des données du dialogue...")
        try:
            width = float(self.width_var.get())
            height = float(self.height_var.get())
            unit = self.unit_var.get()

            if width <= 0 or height <= 0:
                messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), self.language_manager.get_text('invalid_dimension_message', 'Please enter valid positive dimensions.'), parent=self.top)
                return

            self.preference_manager.set_physical_dimensions(width, height, unit)
            self.preference_manager.set_screen_config_verified(True)
            dpi = self.preference_manager.calculate_and_set_dpi()
            
            msg = self.language_manager.get_text('config_saved_success', 'Configuration saved successfully.')
            if dpi:
                msg += f" {self.language_manager.get_text('calculated_dpi_label', 'Calculated DPI:')} {dpi:.2f}"
            messagebox.showinfo(self.language_manager.get_text('config_saved_title', 'Configuration Saved'), msg, parent=self.top)
            self.logger.info("Configuration sauvegardée avec succès depuis le dialogue.")
            self.on_closing(close_app=False)

        except ValueError:
            self.logger.warning("Erreur de valeur lors de la validation du dialogue.", exc_info=True)
            messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), self.language_manager.get_text('invalid_numeric_input', 'Please enter numeric values for width and height.'), parent=self.top)
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la validation: {e}", exc_info=True)
            messagebox.showerror(self.language_manager.get_text('error_title', 'Error'), f"{self.language_manager.get_text('an_error_occurred', 'An error occurred')}: {e}", parent=self.top)


    def on_closing(self, close_app=True):
        self.logger.debug(f"Tentative de fermeture du dialogue. close_app={close_app}, screen_config_verified={self.preference_manager.get_screen_config_verified()}")
        if not self.preference_manager.get_screen_config_verified() and close_app:
            if messagebox.askyesno(self.language_manager.get_text('exit_app_title', 'Exit Application'), 
                                     self.language_manager.get_text('exit_app_prompt', 'Screen dimensions are crucial for accurate tracking. Do you want to exit the application?'),
                                     parent=self.top):
                self.logger.warning("L'utilisateur a choisi de quitter l'application car le dialogue n'a pas été validé.")
                if self.parent: # self.parent est self.root
                    self.parent.destroy() 
            else:
                self.logger.info("L'utilisateur a choisi de ne pas quitter, le dialogue reste ouvert.")
                return 
        
        self.logger.info("Fermeture du dialogue FirstLaunch.")
        self.top.destroy()