# main.py

import tkinter as tk
from tkinter import messagebox, PhotoImage
import os
import sys
import logging

# --- AJOUT : Définition de la fonction resource_path ---
def resource_path(relative_path: str) -> str:
    """
    Obtient le chemin absolu vers une ressource, fonctionne pour le développement
    et pour les exécutables créés par PyInstaller.
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke son chemin dans _MEIPASS
        base_path = sys._MEIPASS # type: ignore # type: ignore pour _MEIPASS qui n'est pas connu par les linters
    except Exception:
        # En développement, _MEIPASS n'est pas défini, utiliser le chemin du script
        base_path = os.path.abspath(".") # Ou os.path.dirname(os.path.abspath(__file__)) si main.py n'est pas à la racine

    return os.path.join(base_path, relative_path)
# --- FIN DE L'AJOUT ---

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

# Add gui directory to system path - Assurez-vous que c'est toujours nécessaire avec votre structure
gui_path = os.path.join(os.path.dirname(__file__), 'gui')
if gui_path not in sys.path:
    sys.path.append(gui_path)


class MouseTrackerApp:
    """
    Classe principale de l'application Mouse Tracker.
    Gère le cycle de vie de l'application.
    """
    def __init__(self, root):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initialisation de MouseTrackerApp...")
        self.root = root
        self.root.withdraw() 

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

        if self.preference_manager and self.preference_manager.get_show_first_launch_dialog():
            self._show_first_launch_dialog() 
        else:
            self.root.deiconify() 
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
        # La langue est maintenant gérée au chargement de MainWindow ou FirstLaunchDialog
        # self.language_manager.set_language(preference_manager.get_language()) # Peut être redondant

        stats_manager = StatsManager()
        service_locator.register_service("stats_manager", stats_manager)
        self.stats_manager = stats_manager

        if self.preference_manager: # Vérifier si preference_manager est initialisé
            if not self.preference_manager.get_screen_config_verified() or \
               (self.preference_manager.get_physical_width_cm() == 0.0 and self.preference_manager.get_physical_height_cm() == 0.0):
                self.logger.info("Configuration DPI différée (écran non configuré ou non vérifié).")
            else:
                # Le DPI est calculé et stocké par PreferenceManager.
                # On peut logger le DPI chargé si besoin.
                # self.preference_manager.calculate_and_set_dpi() # Recalculer ici est peut-être inutile
                self.logger.info(f"DPI actuel chargé depuis les préférences: {self.preference_manager.get_dpi():.2f}")
        self.logger.info("Services initialisés.")

    def _initialize_input_manager(self):
        """Initialise et démarre InputManager."""
        self.logger.info("Initialisation de InputManager...")
        input_manager = InputManager()
        service_locator.register_service("input_manager", input_manager)
        self.input_manager = input_manager
        if self.input_manager:
            self.input_manager.start_tracking()
            self.logger.info("InputManager démarré.")
        else:
            self.logger.error("Échec de l'initialisation de InputManager.")


    def _initialize_systray(self):
        """Initialise et démarre le SystrayManager."""
        self.logger.info("Initialisation du SystrayManager...")
        if not self.language_manager:
            self.logger.error("LanguageManager non disponible pour initialiser SystrayManager.")
            return

        app_title = self.language_manager.get_text('app_title', 'Mouse Tracker')
        
        # --- MODIFIÉ : Utilisation de resource_path pour l'icône du systray ---
        icon_path_relative = os.path.join('assets', 'icons', 'systray_icon.ico')
        icon_path_abs = resource_path(icon_path_relative)
        # --- FIN DE LA MODIFICATION ---

        self.systray_manager = SystrayManager(
            root_tk_object=self.root,
            app_title=app_title,
            icon_path=icon_path_abs, # Utiliser le chemin absolu résolu
            language_manager=self.language_manager,
            on_show_window_callback=self._show_window,
            on_quit_application_callback=self._quit_app_from_systray
        )
        if self.systray_manager:
            self.systray_manager.start()
            if not self.systray_manager.is_running:
                self.logger.warning("SystrayManager n'a pas pu démarrer.")
            else:
                self.logger.info("SystrayManager démarré.")
        else:
            self.logger.error("Échec de l'initialisation de SystrayManager.")


    def _show_first_launch_dialog(self):
        """Affiche le dialogue de configuration du premier lancement."""
        self.logger.info("Préparation affichage dialogue premier lancement.")
        
        lang_mgr = service_locator.get_service("language_manager")
        pref_mgr = service_locator.get_service("preference_manager")

        if not lang_mgr or not pref_mgr:
            self.logger.error("LanguageManager ou PreferenceManager non disponible pour FirstLaunchDialog.")
            self.root.deiconify()
            return

        dialog = FirstLaunchDialog(self.root, lang_mgr, pref_mgr)
        self.logger.info("Dialogue premier lancement créé, en attente de fermeture...")
        self.root.wait_window(dialog.top) 
        self.logger.info("Dialogue premier lancement fermé.")

        self.root.deiconify() 
        self.logger.info("Fenêtre principale affichée après le dialogue.")

        if self.main_window:
            self.main_window.load_language() 
            self.main_window.update_stats_display() 

        if self.preference_manager:
            self.preference_manager.set_show_first_launch_dialog(False)
            self.logger.info("Préférence 'show_first_launch_dialog' mise à False.")

    def _show_window(self):
        """Restaure et amène la fenêtre principale au premier plan."""
        self.logger.debug("Affichage fenêtre principale (via _show_window).")
        if self.root and self.root.winfo_exists():
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(50, lambda: self.root.attributes('-topmost', False))
            self.root.focus_force()
        else:
            self.logger.warning("Tentative d'affichage sur une fenêtre racine détruite ou inexistante.")


    def _hide_window(self):
        """Cache la fenêtre principale."""
        self.logger.debug("Masquage fenêtre principale.")
        if self.root and self.root.winfo_exists():
            self.root.withdraw()
        else:
            self.logger.warning("Tentative de masquage d'une fenêtre racine détruite ou inexistante.")

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

    def _shutdown_application_components(self, from_systray_thread=False):
        """Arrête proprement les différents composants de l'application."""
        self.logger.info("Début de l'arrêt des composants de l'application...")
        if self.main_window and hasattr(self.main_window, 'stop_update_loop'):
            self.main_window.stop_update_loop()
        
        if self.input_manager:
            self.input_manager.stop_tracking()
            self.logger.info("InputManager arrêté.")
        
        if self.stats_manager:
            self.stats_manager.close()
            self.logger.info("StatsManager fermé.")
            
        if self.systray_manager:
            if from_systray_thread:
                self.systray_manager.signal_icon_to_stop()
            else:
                self.systray_manager.stop() 
            self.logger.info("SystrayManager signalé pour arrêt ou arrêté.")


    def _quit_app_from_systray(self):
        """Callback pour l'arrêt initié depuis SystrayManager."""
        self.logger.info("Callback arrêt depuis SystrayManager (thread systray).")
        if self.root:
            self.root.after_idle(self._shutdown_application_components, True)
            self.root.after_idle(self._perform_tk_shutdown)
        else: # Fallback si root est déjà détruit
            self._shutdown_application_components(True)


    def _quit_app_cleanly(self):
        """Arrêt gracieux complet (appelé depuis le thread principal)."""
        self.logger.info("Lancement procédure arrêt propre (thread principal attendu).")
        self._shutdown_application_components()
        self._perform_tk_shutdown()

    def _on_closing(self):
        """Gère l'action du bouton de fermeture de la fenêtre principale."""
        self.logger.debug("Action de fermeture de la fenêtre principale (WM_DELETE_WINDOW).")
        systray_active_and_can_minimize = self.systray_manager and self.systray_manager.is_running # Simplifié pour l'instant
        # Pour une vraie option "minimize_to_tray_on_close", il faudrait la lire depuis PreferenceManager

        if systray_active_and_can_minimize:
            self.logger.info("Fermeture vers barre système.")
            self._hide_window()
        else:
            self.logger.info("Systray non actif ou option de minimisation désactivée, demande confirmation pour quitter.")
            title = "Quitter l'application"
            message = "Êtes-vous sûr de vouloir quitter ?"
            if self.language_manager:
                title = self.language_manager.get_text('exit_app_title', 'Exit Application')
                message_key = 'exit_app_prompt_no_systray_available' if not (self.systray_manager and self.systray_manager.is_running) else 'exit_app_prompt_confirm_exit'
                default_message = 'Systray icon is not available. Exit completely?' if message_key == 'exit_app_prompt_no_systray_available' else 'Are you sure you want to exit?'
                message = self.language_manager.get_text(message_key, default_message)
            
            if messagebox.askyesno(title, message, parent=self.root if self.root and self.root.winfo_exists() else None):
                self.logger.info("Utilisateur a choisi de quitter via dialogue.")
                self._quit_app_cleanly()
            else:
                self.logger.info("Utilisateur a annulé la fermeture.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
    )
    
    logging.getLogger('gui.main_window').setLevel(logging.INFO)
    logging.getLogger('managers.stats_manager').setLevel(logging.INFO)
    # Ajouter ici si d'autres loggers deviennent trop verbeux en DEBUG
    # logging.getLogger('gui.history_tab').setLevel(logging.INFO) 

    main_logger = logging.getLogger(__name__)
    main_logger.info("Démarrage application Mouse Tracker (__main__).")

    # --- MODIFIÉ : Utilisation de resource_path pour l'icône principale de la fenêtre ---
    # Le chemin relatif est par rapport à la racine du projet si base_path est os.path.abspath(".")
    # ou par rapport à _MEIPASS si packagé.
    icon_path_main_relative = os.path.join('assets', 'icons', 'systray_icon.ico') 
    icon_path_main_abs = resource_path(icon_path_main_relative)
    # --- FIN DE LA MODIFICATION ---

    root = tk.Tk()

    try:
        if not os.path.exists(icon_path_main_abs): # Vérifier le chemin absolu résolu
             main_logger.warning(f"Fichier icône Tkinter non trouvé: {icon_path_main_abs}.")
        elif os.name == 'nt':
            main_logger.debug(f"Chargement icône (.ico) Windows: {icon_path_main_abs}")
            root.iconbitmap(default=icon_path_main_abs)
        else:
            main_logger.debug(f"Chargement icône (PhotoImage) Linux/macOS: {icon_path_main_abs}")
            try:
                icon_img = PhotoImage(file=icon_path_main_abs)
                root.iconphoto(False, icon_img)
            except tk.TclError as e_img: # Attraper spécifiquement TclError
                main_logger.warning(f"Impossible charger PhotoImage: {icon_path_main_abs}. Erreur: {e_img}. Format .png suggéré.")
    except tk.TclError as e: # Erreur plus générale de Tcl pour iconbitmap
        main_logger.warning(f"Impossible charger icône Tkinter (TclError): {icon_path_main_abs}: {e}", exc_info=True)
    # FileNotFoundError est déjà géré par le if os.path.exists() plus haut pour icon_path_main_abs
    # except FileNotFoundError: 
    #    main_logger.warning(f"Fichier icône Tkinter non trouvé (FileNotFoundError): {icon_path_main_abs}.")
    except Exception as e_icon_generic: # Attraper d'autres exceptions inattendues
        main_logger.error(f"Erreur inattendue lors du chargement de l'icône Tkinter: {e_icon_generic}", exc_info=True)


    app = None # Pour le bloc finally
    try:
        app = MouseTrackerApp(root)
        main_logger.info("Application initialisée, lancement boucle Tkinter.")
        root.mainloop()
    except KeyboardInterrupt:
        main_logger.info("Arrêt de l'application par KeyboardInterrupt.")
        # Gérer l'arrêt propre si app a été initialisé
        if app and hasattr(app, '_quit_app_cleanly'):
             app._quit_app_cleanly()
    except Exception as e:
        main_logger.critical(f"Erreur non gérée fatale: {e}", exc_info=True)
        # Tenter un arrêt propre même en cas d'erreur fatale
        if app and hasattr(app, '_quit_app_cleanly'):
            try:
                app._quit_app_cleanly()
            except Exception as e_shutdown:
                main_logger.error(f"Erreur lors de la tentative d'arrêt propre après une erreur fatale: {e_shutdown}", exc_info=True)
    finally:
        main_logger.info("Application TrackMyMouse terminée ou tentative de terminaison.")