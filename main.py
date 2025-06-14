# main.py

import tkinter as tk
from tkinter import messagebox, PhotoImage
import os
import sys
import logging
from typing import Optional

# --- MODIFIÉ : Import des nouvelles fonctions de gestion de chemin ---
from utils.paths import get_icon_path 

# Core application services and managers
from utils.event_manager import event_manager
from managers.activity_tracker import ActivityTracker
from utils.service_locator import service_locator
from managers.language_manager import LanguageManager
from managers.stats_manager import StatsManager
from managers.preference_manager import PreferenceManager
from managers.input_manager import InputManager
from managers.systray_manager import SystrayManager

# GUI components
from gui.main_window import MainWindow
from gui.first_launch_dialog import FirstLaunchDialog

# La modification du sys.path peut ne pas être nécessaire si vous lancez
# votre application comme un module depuis la racine (ex: python -m main).
# Pour l'instant, nous la conservons car elle assure que ça fonctionne dans votre configuration actuelle.
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

        # Initialisation des managers à None, seront définis dans _initialize_services
        self.language_manager: Optional[LanguageManager] = None
        self.stats_manager: Optional[StatsManager] = None
        self.preference_manager: Optional[PreferenceManager] = None
        self.input_manager: Optional[InputManager] = None
        self.systray_manager: Optional[SystrayManager] = None

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
        try:
            self.preference_manager = PreferenceManager()
            service_locator.register_service("preference_manager", self.preference_manager)

            self.language_manager = LanguageManager() 
            service_locator.register_service("language_manager", self.language_manager)
            service_locator.register_service("event_manager", event_manager)

            self.stats_manager = StatsManager()
            service_locator.register_service("stats_manager", self.stats_manager)

            self.activity_tracker = ActivityTracker()
            self.activity_tracker.start()

            self.logger.info("Services initialisés.")
        except Exception as e:
            self.logger.critical(f"Erreur critique lors de l'initialisation des services: {e}", exc_info=True)
            messagebox.showerror("Erreur Critique", f"Impossible d'initialiser les services de l'application: {e}")
            self.root.quit()
            
    def _initialize_input_manager(self):
        """Initialise et démarre InputManager."""
        self.logger.info("Initialisation de InputManager...")
        try:
            self.input_manager = InputManager()
            service_locator.register_service("input_manager", self.input_manager)
            self.input_manager.start_tracking()
            self.logger.info("InputManager démarré.")
        except Exception as e:
            self.logger.error(f"Échec de l'initialisation ou du démarrage de InputManager: {e}", exc_info=True)

    def _initialize_systray(self):
        """Initialise et démarre le SystrayManager."""
        self.logger.info("Initialisation du SystrayManager...")
        if not self.language_manager:
            self.logger.error("LanguageManager non disponible pour initialiser SystrayManager.")
            return

        try:
            app_title = self.language_manager.get_text('app_title', 'Mouse Tracker')
            
            # --- MODIFIÉ : Utilisation de get_icon_path() ---
            icon_path = get_icon_path()
            
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
        except Exception as e:
            self.logger.error(f"Échec de l'initialisation de SystrayManager: {e}", exc_info=True)

    def _show_first_launch_dialog(self):
        """Affiche le dialogue de configuration du premier lancement."""
        self.logger.info("Préparation affichage dialogue premier lancement.")
        
        try:
            lang_mgr = service_locator.get_service("language_manager")
            pref_mgr = service_locator.get_service("preference_manager")

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
        except Exception as e:
            self.logger.error(f"Erreur lors de l'affichage du dialogue de premier lancement: {e}", exc_info=True)
            if self.root and self.root.winfo_exists():
                 self.root.deiconify()

    def _show_window(self):
        """Restaure et amène la fenêtre principale au premier plan."""
        if not (self.root and self.root.winfo_exists()):
            self.logger.warning("Tentative d'affichage sur une fenêtre racine inexistante.")
            return
        self.logger.debug("Affichage fenêtre principale (via _show_window).")
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(50, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()

    def _hide_window(self):
        """Cache la fenêtre principale."""
        self.logger.debug("Masquage fenêtre principale.")
        if self.root and self.root.winfo_exists():
            self.root.withdraw()

    def _perform_tk_shutdown(self):
        """Effectue la fermeture propre de Tkinter."""
        self.logger.info("Arrêt interface Tkinter...")
        try:
            if self.root and self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()
                self.logger.info("Interface Tkinter arrêtée.")
        except Exception as e:
            self.logger.error(f"Erreur arrêt Tkinter : {e}", exc_info=True)
    
    def _shutdown_application_components(self, from_systray_thread=False):
        """Arrête proprement les différents composants de l'application."""
        self.logger.info("Début de l'arrêt des composants de l'application...")
        if self.main_window: self.main_window.stop_update_loop()
        if self.input_manager: self.input_manager.stop_tracking()
        if hasattr(self, 'activity_tracker'): self.activity_tracker.stop()
        if self.stats_manager: self.stats_manager.close()
        if self.systray_manager:
            if from_systray_thread: self.systray_manager.signal_icon_to_stop()
            else: self.systray_manager.stop() 
        self.logger.info("Arrêt des composants terminé.")

    def _quit_app_from_systray(self):
        """Callback pour l'arrêt initié depuis SystrayManager (thread systray)."""
        self.logger.info("Arrêt de l'application initié depuis systray.")
        if self.root:
            self.root.after_idle(self._shutdown_application_components, True)
            self.root.after_idle(self._perform_tk_shutdown)

    def _quit_app_cleanly(self):
        """Arrêt gracieux complet (appelé depuis le thread principal)."""
        self.logger.info("Lancement procédure arrêt propre.")
        self._shutdown_application_components()
        self._perform_tk_shutdown()

    def _on_closing(self):
        """Gère l'action du bouton de fermeture de la fenêtre principale."""
        self.logger.debug("Action de fermeture de la fenêtre principale (WM_DELETE_WINDOW).")
        systray_active = self.systray_manager and self.systray_manager.is_running
        
        if systray_active:
            self.logger.info("Fermeture vers barre système.")
            self._hide_window()
        else:
            self.logger.warning("Systray non actif. Demande confirmation pour quitter.")
            title = "Quitter l'application"
            message = "Êtes-vous sûr de vouloir quitter ?"
            if self.language_manager:
                title = self.language_manager.get_text('exit_app_title', 'Exit Application')
                message_key = 'exit_app_prompt_no_systray_available' if not systray_active else 'exit_app_prompt_confirm_exit'
                default_message = 'Systray icon is not available. Exit completely?' if message_key == 'exit_app_prompt_no_systray_available' else 'Are you sure you want to exit?'
                message = self.language_manager.get_text(message_key, default_message)
            
            if messagebox.askyesno(title, message, parent=self.root):
                self.logger.info("Utilisateur a confirmé la fermeture complète.")
                self._quit_app_cleanly()
            else:
                self.logger.info("Fermeture annulée par l'utilisateur.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
    )
    
    logging.getLogger('gui.main_window').setLevel(logging.INFO)
    logging.getLogger('managers.stats_manager').setLevel(logging.INFO)
    logging.getLogger('gui.history_tab').setLevel(logging.INFO)
    logging.getLogger('managers.stats_repository').setLevel(logging.INFO)

    main_logger = logging.getLogger(__name__)
    main_logger.info("Démarrage application TrackMyMouse (__main__).")

    # --- MODIFIÉ : Utilisation de get_icon_path() ---
    icon_path_main = get_icon_path()
    # --- FIN DE LA MODIFICATION ---

    root = tk.Tk()

    try:
        if not os.path.exists(icon_path_main):
            main_logger.warning(f"Fichier icône Tkinter non trouvé: {icon_path_main}.")
        elif os.name == 'nt':
            main_logger.debug(f"Chargement icône (.ico) Windows: {icon_path_main}")
            root.iconbitmap(default=icon_path_main)
        else:
            main_logger.debug(f"Chargement icône (PhotoImage) Linux/macOS: {icon_path_main}")
            try:
                icon_img = PhotoImage(file=icon_path_main)
                root.iconphoto(False, icon_img)
            except tk.TclError as e_img:
                main_logger.warning(f"Impossible de charger PhotoImage: {icon_path_main}. Erreur: {e_img}.")
    except Exception as e_icon_generic:
        main_logger.error(f"Erreur inattendue lors du chargement de l'icône Tkinter: {e_icon_generic}", exc_info=True)

    app = None
    try:
        app = MouseTrackerApp(root)
        main_logger.info("Application initialisée, lancement boucle Tkinter.")
        root.mainloop()
    except KeyboardInterrupt:
        main_logger.info("Arrêt de l'application par KeyboardInterrupt.")
    except Exception as e:
        main_logger.critical(f"Erreur non gérée fatale: {e}", exc_info=True)
    finally:
        # La logique de nettoyage est maintenant appelée via les callbacks de fermeture
        main_logger.info("Fin du bloc __main__ de l'application TrackMyMouse.")