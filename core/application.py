# core/application.py

from tkinter import messagebox
import logging

from utils.paths import get_icon_path
from core.app_builder import AppBuilder

from managers.systray_manager import SystrayManager

from gui.main_window import MainWindow
from gui.first_launch_dialog import FirstLaunchDialog

logger = logging.getLogger(__name__)

class MouseTrackerApp:
    """
    Classe principale de l'application Mouse Tracker.
    Gère le cycle de vie de l'application.
    """
    def __init__(self, root):
        logger.info("Initialisation de MouseTrackerApp...")
        self.root = root
        self.root.withdraw() 

        # --- MODIFICATION MAJEURE : Utilisation de l'AppBuilder ---
        # 1. On utilise le builder pour construire tous les services.
        builder = AppBuilder()
        self.services = builder.build()

        # 2. On assigne les managers nécessaires comme attributs pour un accès facile.
        self.config_manager = self.services.get('config_manager')
        self.language_manager = self.services.get('language_manager')
        self.stats_manager = self.services.get('stats_manager')
        self.input_manager = self.services.get('input_manager')
        self.xp_manager = self.services.get('xp_manager')
        self.activity_tracker = self.services.get('activity_tracker')
        # -----------------------------------------------------------

        # La création de l'UI et du systray reste de la responsabilité de l'application
        self.main_window = MainWindow(self.root)
        self.main_window.pack(expand=True, fill='both')
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._initialize_systray()

        # Logique de démarrage
        if self.config_manager and self.config_manager.get_show_first_launch_dialog():
            self._show_first_launch_dialog() 
        else:
            self.root.deiconify() 
            logger.info("Fenêtre principale affichée (dialogue premier lancement non requis).")
            
        logger.info("MouseTrackerApp initialisée avec succès.")
    
    def _initialize_systray(self):
        """Initialise et démarre le SystrayManager."""
        logger.info("Initialisation du SystrayManager...")
        if not self.language_manager:
            logger.error("LanguageManager non disponible pour initialiser SystrayManager.")
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
                logger.warning("SystrayManager n'a pas pu démarrer.")
            else:
                logger.info("SystrayManager démarré.")
        except Exception as e:
            logger.error(f"Échec de l'initialisation de SystrayManager: {e}", exc_info=True)

    def _show_first_launch_dialog(self):
        """Affiche le dialogue de configuration du premier lancement."""
        logger.info("Préparation affichage dialogue premier lancement.")
        
        try:
            dialog = FirstLaunchDialog(self.root)
            logger.info("Dialogue premier lancement créé, en attente de fermeture...")
            self.root.wait_window(dialog.top) 
            logger.info("Dialogue premier lancement fermé.")

            self.root.deiconify() 
            logger.info("Fenêtre principale affichée après le dialogue.")

            if self.main_window:
                self.main_window.load_language() 
                        
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du dialogue de premier lancement: {e}", exc_info=True)
            if self.root and self.root.winfo_exists():
                 self.root.deiconify()

    def _show_window(self):
        """Restaure et amène la fenêtre principale au premier plan."""
        if not (self.root and self.root.winfo_exists()):
            logger.warning("Tentative d'affichage sur une fenêtre racine inexistante.")
            return
        logger.debug("Affichage fenêtre principale (via _show_window).")
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(50, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()

    def _hide_window(self):
        """Cache la fenêtre principale."""
        logger.debug("Masquage fenêtre principale.")
        if self.root and self.root.winfo_exists():
            self.root.withdraw()

    def _perform_tk_shutdown(self):
        """Effectue la fermeture propre de Tkinter."""
        logger.info("Arrêt interface Tkinter...")
        try:
            if self.root and self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()
                logger.info("Interface Tkinter arrêtée.")
        except Exception as e:
            logger.error(f"Erreur arrêt Tkinter : {e}", exc_info=True)
    
    def _shutdown_application_components(self, from_systray_thread=False):
        """Arrête proprement les différents composants de l'application."""
        logger.info("Début de l'arrêt des composants de l'application...")
        if self.main_window: self.main_window.stop_update_loop()
        if self.input_manager: self.input_manager.stop_tracking()
        if hasattr(self, 'activity_tracker'): self.activity_tracker.stop()
        if self.xp_manager: self.xp_manager.stop()
        if self.stats_manager: self.stats_manager.close()
        if self.systray_manager:
            if from_systray_thread: self.systray_manager.signal_icon_to_stop()
            else: self.systray_manager.stop() 
        logger.info("Arrêt des composants terminé.")

    def _quit_app_from_systray(self):
        """Callback pour l'arrêt initié depuis SystrayManager (thread systray)."""
        logger.info("Arrêt de l'application initié depuis systray.")
        if self.root:
            self.root.after_idle(self._shutdown_application_components, True)
            self.root.after_idle(self._perform_tk_shutdown)

    def _quit_app_cleanly(self):
        """Arrêt gracieux complet (appelé depuis le thread principal)."""
        logger.info("Lancement procédure arrêt propre.")
        self._shutdown_application_components()
        self._perform_tk_shutdown()

    def _on_closing(self):
        """Gère l'action du bouton de fermeture de la fenêtre principale."""
        logger.debug("Action de fermeture de la fenêtre principale (WM_DELETE_WINDOW).")
        systray_active = self.systray_manager and self.systray_manager.is_running
        
        if systray_active:
            logger.info("Fermeture vers barre système.")
            self._hide_window()
        else:
            logger.warning("Systray non actif. Demande confirmation pour quitter.")
            title = "Quitter l'application"
            message = "Êtes-vous sûr de vouloir quitter ?"
            if self.language_manager:
                title = self.language_manager.get_text('exit_app_title', 'Exit Application')
                message_key = 'exit_app_prompt_no_systray_available' if not systray_active else 'exit_app_prompt_confirm_exit'
                default_message = 'Systray icon is not available. Exit completely?' if message_key == 'exit_app_prompt_no_systray_available' else 'Are you sure you want to exit?'
                message = self.language_manager.get_text(message_key, default_message)
            
            if messagebox.askyesno(title, message, parent=self.root):
                logger.info("Utilisateur a confirmé la fermeture complète.")
                self._quit_app_cleanly()
            else:
                logger.info("Fermeture annulée par l'utilisateur.")