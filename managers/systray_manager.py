# managers/systray_manager.py

import threading
import logging
from PIL import Image
import pystray # type: ignore

class SystrayManager:
    """
    Gère l'icône de la barre système (systray), son menu et ses actions.
    """
    def __init__(self,
                 root_tk_object, # <--- AJOUT: référence à l'objet root de Tkinter
                 app_title: str,
                 icon_path: str,
                 language_manager,
                 on_show_window_callback,
                 on_quit_application_callback
                 ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.root_tk_object = root_tk_object # <--- AJOUT
        self.app_title = app_title
        self.icon_path = icon_path
        self.language_manager = language_manager
        self.on_show_window_callback = on_show_window_callback
        self.on_quit_application_callback = on_quit_application_callback

        self.pystray_icon = None
        self.thread = None
        self.is_running = False

        self.logger.info("SystrayManager initialisé.")

    def start(self):
        if self.is_running:
            self.logger.warning("SystrayManager déjà en cours d'exécution.")
            return

        self.logger.info("Démarrage de l'icône systray...")
        try:
            image = Image.open(self.icon_path)
            menu = self._build_menu()
            
            self.pystray_icon = pystray.Icon(
                name=self.app_title,
                icon=image,
                title=self.app_title,
                menu=menu
            )
            
            self.thread = threading.Thread(target=self._run_icon, daemon=True)
            self.thread.start()
            self.is_running = True
            self.logger.info("Icône systray démarrée.")

        except FileNotFoundError:
            self.logger.error(f"Fichier icône '{self.icon_path}' non trouvé. L'icône systray ne sera pas affichée.")
        except Exception as e:
            self.logger.error(f"Erreur création icône systray: {e}", exc_info=True)
            
    def stop(self):
        if not self.is_running or not self.pystray_icon:
            self.logger.info("SystrayManager non actif ou icône inexistante.")
            return

        self.logger.info("Arrêt de l'icône systray...")
        self.pystray_icon.stop()
        
        if self.thread and self.thread.is_alive():
            self.logger.debug("Attente fin thread systray...")
            self.thread.join(timeout=2.0)
            if self.thread.is_alive():
                self.logger.warning("Thread systray non arrêté dans le délai.")
            else:
                self.logger.debug("Thread systray terminé.")
        
        self.is_running = False
        self.logger.info("SystrayManager arrêté.")

    def signal_icon_to_stop(self):
        if self.pystray_icon and self.is_running:
            self.logger.debug("Signal interne d'arrêt à pystray.")
            self.pystray_icon.stop()
        self.is_running = False

    def _run_icon(self):
        if self.pystray_icon:
            try:
                self.pystray_icon.run()
            except Exception as e:
                self.logger.error(f"Erreur dans pystray.Icon.run(): {e}", exc_info=True)
            finally:
                self.is_running = False
                self.logger.info("Exécution pystray.Icon.run() terminée.")

    def _build_menu(self):
        open_text = self.language_manager.get_text('tray_open_app', 'Open')
        quit_text = self.language_manager.get_text('tray_quit_app', 'Quit')

        menu = pystray.Menu(
            pystray.MenuItem(open_text, self._on_menu_show_window, default=True),
            pystray.MenuItem(quit_text, self._on_menu_quit_application)
        )
        return menu

    def _on_menu_show_window(self, icon, item):
        self.logger.debug("Action 'Afficher la fenêtre' (systray).")
        if self.on_show_window_callback and self.root_tk_object:
            # Planifier l'appel dans le thread principal de Tkinter
            self.root_tk_object.after_idle(self.on_show_window_callback) # <--- MODIFIÉ
        elif not self.root_tk_object:
            self.logger.error("Référence à root_tk_object manquante dans SystrayManager pour _on_menu_show_window.")


    def _on_menu_quit_application(self, icon, item):
        self.logger.debug("Action 'Quitter l'application' (systray).")
        if self.on_quit_application_callback:
            self.on_quit_application_callback()