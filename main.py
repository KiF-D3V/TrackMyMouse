# main.py

import tkinter as tk
from tkinter import messagebox, PhotoImage
import os
import sys
import logging

# Core application services and managers
from utils.service_locator import service_locator
from managers.language_manager import LanguageManager
from managers.stats_manager import StatsManager
from config.preference_manager import PreferenceManager
from managers.input_manager import InputManager
from managers.systray_manager import SystrayManager

# GUI components
from gui.main_window import MainWindow
from gui.first_launch_dialog import FirstLaunchDialog

# Add gui directory to system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui'))

class MouseTrackerApp:
    """
    Classe principale de l'application Mouse Tracker.
    Gère le cycle de vie de l'application.
    """
    def __init__(self, root):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initialisation de MouseTrackerApp...")
        self.root = root
        self.root.withdraw() # Cacher la fenêtre principale au début

        self.language_manager = None
        self.stats_manager = None
        self.preference_manager = None
        self.input_manager = None
        self.systray_manager = None

        self._initialize_services()
        self._initialize_input_manager()

        self.main_window = MainWindow(self.root)
        self.main_window.pack(expand=True, fill='both')

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._initialize_systray()

        # Gérer le dialogue de premier lancement et la visibilité de la fenêtre principale
        if self.preference_manager.get_show_first_launch_dialog():
            self._show_first_launch_dialog() # Cette méthode s'occupera de réafficher root au bon moment
        else:
            self.root.deiconify() # Réafficher si pas de dialogue
            self.logger.info("Fenêtre principale affichée (dialogue premier lancement non requis).")
            
        self.logger.info("MouseTrackerApp initialisée avec succès.")

    def _initialize_services(self):
        """Initialise les gestionnaires principaux de l'application."""
        self.logger.info("Initialisation des services...")
        preference_manager = PreferenceManager()
        service_locator.register_service("preference_manager", preference_manager)
        self.preference_manager = preference_manager

        language_manager = LanguageManager()
        service_locator.register_service("language_manager", language_manager)
        self.language_manager = language_manager
        self.language_manager.set_language(preference_manager.get_language())

        stats_manager = StatsManager()
        service_locator.register_service("stats_manager", stats_manager)
        self.stats_manager = stats_manager

        if not preference_manager.get_screen_config_verified() or \
           (preference_manager.get_physical_width_cm() == 0.0 and preference_manager.get_physical_height_cm() == 0.0):
            self.logger.info("Configuration DPI différée.")
        else:
            preference_manager.calculate_and_set_dpi()
        self.logger.info("Services initialisés.")

    def _initialize_input_manager(self):
        """Initialise et démarre InputManager."""
        self.logger.info("Initialisation de InputManager...")
        input_manager = InputManager()
        service_locator.register_service("input_manager", input_manager)
        self.input_manager = input_manager
        self.input_manager.start_tracking()
        self.logger.info("InputManager démarré.")

    def _initialize_systray(self):
        """Initialise et démarre le SystrayManager."""
        self.logger.info("Initialisation du SystrayManager...")
        app_title = self.language_manager.get_text('app_title', 'Mouse Tracker')
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'assets', 'icons', 'systray_icon.ico')

        self.systray_manager = SystrayManager(
            root_tk_object=self.root,
            app_title=app_title,
            icon_path=icon_path,
            language_manager=self.language_manager,
            on_show_window_callback=self._show_window,
            on_quit_application_callback=self._quit_app_from_systray
        )
        self.systray_manager.start()
        if not self.systray_manager.is_running:
            self.logger.warning("SystrayManager n'a pas pu démarrer.")
        else:
            self.logger.info("SystrayManager démarré.")

    def _show_first_launch_dialog(self):
        """Affiche le dialogue de configuration du premier lancement."""
        self.logger.info("Préparation affichage dialogue premier lancement (fenêtre principale initialement cachée).")
        # self.root.deiconify() # <--- ERREUR DE LA VERSION PRÉCÉDENTE, SUPPRIMÉE CORRECTEMENT ICI.
                                 # self.root est déjà withdrawn, le dialogue Toplevel devrait s'afficher seul.

        lang_mgr = service_locator.get_service("language_manager")
        pref_mgr = service_locator.get_service("preference_manager")

        dialog = FirstLaunchDialog(self.root, lang_mgr, pref_mgr)
        self.logger.info("Dialogue premier lancement créé, en attente de fermeture...")
        self.root.wait_window(dialog.top) # Attend la fermeture du dialogue
        self.logger.info("Dialogue premier lancement fermé.")

        # Maintenant que le dialogue est fermé, afficher la fenêtre principale
        self.root.deiconify() 
        self.logger.info("Fenêtre principale affichée après le dialogue.")

        self.main_window.load_language() 
        self.main_window.update_stats_display() 

        self.preference_manager.set_show_first_launch_dialog(False)
        self.logger.info("Préférence 'show_first_launch_dialog' mise à False.")

    def _show_window(self):
        """Restaure et amène la fenêtre principale au premier plan."""
        self.logger.debug("Affichage fenêtre principale (via _show_window).")
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(50, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()

    def _hide_window(self):
        """Cache la fenêtre principale."""
        self.logger.debug("Masquage fenêtre principale.")
        self.root.withdraw()

    def _perform_tk_shutdown(self):
        """Effectue la fermeture propre de Tkinter."""
        self.logger.info("Arrêt interface Tkinter...")
        try:
            if self.root and self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()
                self.logger.info("Interface Tkinter arrêtée.")
            else:
                self.logger.warning("Fenêtre racine Tkinter n'existe plus ou ne peut être arrêtée.")
        except Exception as e:
            self.logger.error(f"Erreur arrêt Tkinter : {e}", exc_info=True)

    def _quit_app_from_systray(self):
        """Callback pour l'arrêt initié depuis SystrayManager."""
        self.logger.info("Callback arrêt depuis SystrayManager (thread systray).")
        if self.main_window: self.main_window.stop_update_loop()
        if self.input_manager: self.input_manager.stop_tracking()
        if self.stats_manager: self.stats_manager.close()
        if self.systray_manager: self.systray_manager.signal_icon_to_stop()
        if self.root: self.root.after_idle(self._perform_tk_shutdown)

    def _quit_app_cleanly(self):
        """Arrêt gracieux complet (appelé depuis le thread principal)."""
        self.logger.info("Lancement procédure arrêt propre (thread principal attendu).")
        if self.main_window: self.main_window.stop_update_loop()
        if self.input_manager: self.input_manager.stop_tracking()
        if self.stats_manager: self.stats_manager.close()
        if self.systray_manager: self.systray_manager.stop() 
        self._perform_tk_shutdown()

    def _on_closing(self):
        """Gère l'action du bouton de fermeture de la fenêtre principale."""
        systray_active = self.systray_manager and self.systray_manager.is_running
        if systray_active:
            self.logger.info("Fermeture vers barre système.")
            self._hide_window()
        else:
            self.logger.warning("Systray non actif/disponible, demande confirmation pour quitter.")
            title = self.language_manager.get_text('exit_app_title', 'Exit Application')
            message_key = 'exit_app_prompt_no_systray_available' if not self.systray_manager or not self.systray_manager.is_running else 'exit_app_prompt_no_minimize'
            default_message = 'Systray icon is not available or minimizing is disabled. Exit completely?'
            message = self.language_manager.get_text(message_key, default_message)
            if messagebox.askyesno(title, message):
                self.logger.info("Utilisateur a choisi de quitter via dialogue.")
                self._quit_app_cleanly()
            else:
                self.logger.info("Utilisateur a annulé la fermeture.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
    )
    main_logger = logging.getLogger(__name__)
    main_logger.info("Démarrage application Mouse Tracker (__main__).")

    # ----- REDUIRE la verbosité de gui.main_window et de managers.stats_manager -----
    logging.getLogger('gui.main_window').setLevel(logging.INFO)
    logging.getLogger('managers.stats_manager').setLevel(logging.INFO)
    # ---------------------------------------------------------------------------------

    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path_main = os.path.join(script_dir, 'assets', 'icons', 'systray_icon.ico')

    root = tk.Tk()

    try:
        if os.name == 'nt':
            main_logger.debug(f"Chargement icône (.ico) Windows: {icon_path_main}")
            root.iconbitmap(default=icon_path_main)
        else:
            main_logger.debug(f"Chargement icône (PhotoImage) Linux/macOS: {icon_path_main}")
            try:
                icon_img = PhotoImage(file=icon_path_main)
                root.iconphoto(False, icon_img)
            except tk.TclError:
                main_logger.warning(f"Impossible charger PhotoImage: {icon_path_main}. Format .png suggéré.")
    except tk.TclError as e:
        main_logger.warning(f"Impossible charger icône Tkinter: {icon_path_main}: {e}", exc_info=True)
    except FileNotFoundError:
        main_logger.warning(f"Fichier icône Tkinter non trouvé: {icon_path_main}.")

    try:
        app = MouseTrackerApp(root)
        main_logger.info("Application initialisée, lancement boucle Tkinter.")
        root.mainloop()
    except Exception as e:
        main_logger.critical(f"Erreur non gérée fatale: {e}", exc_info=True)
    finally:
        main_logger.info("Application Mouse Tracker terminée ou tentative de terminaison.")