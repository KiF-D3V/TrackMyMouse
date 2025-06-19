# managers/input_manager.py

import logging
from pynput.mouse import Listener, Button
from utils.event_manager import event_manager
from utils.service_locator import service_locator

logger = logging.getLogger(__name__)

class InputManager:
    """
    Manages global mouse input events (movements and clicks) using pynput.
    It publishes these events using the EventManager.
    """
    def __init__(self):
        self.mouse_listener = None
        self.is_ready = False
        
        self.event_manager = event_manager
        self.config_manager = service_locator.get_service("config_manager")

        if not self.config_manager:
            logger.error("ConfigManager non disponible. InputManager ne sera pas fonctionnel.")
        else:
            self.is_ready = True
            logger.info("InputManager initialisé.")

    def _on_move(self, x, y):
        """Callback for mouse movement events. Publishes a 'mouse_moved' event."""
        try:
            if self.is_ready and self.config_manager.get_track_mouse_distance():
                self.event_manager.publish('mouse_moved', x=x, y=y)
        except Exception as e:
            logger.error(
                "Une erreur est survenue dans un abonné à l'événement 'mouse_moved'", 
                exc_info=True
            )

    def _on_click(self, x, y, button: Button, pressed: bool):
        """Callback for mouse click events. Publishes a 'mouse_clicked' event on press."""
        try:
            if pressed and self.is_ready and self.config_manager.get_track_mouse_clicks():
                button_name = button.name if hasattr(button, 'name') else 'unknown'
                logger.debug(f"Clic détecté : {button_name}")
                self.event_manager.publish('mouse_clicked', button=button, x=x, y=y) # Note: ajout de x, y
        except Exception as e:
            logger.error(
                f"Une erreur est survenue dans un abonné à l'événement 'mouse_clicked' (bouton: {button})", 
                exc_info=True
            )

    def start_tracking(self):
        """Starts the pynput mouse listener in a separate thread."""
        if not self.is_ready:
            logger.warning("Démarrage du tracking impossible, InputManager non prêt.")
            return

        if self.mouse_listener is None or not self.mouse_listener.is_alive():
            logger.info("Démarrage de l'écoute des événements souris...")
            self.mouse_listener = Listener(
                on_move=self._on_move,
                on_click=self._on_click
            )
            self.mouse_listener.start()

    def stop_tracking(self):
        """Stops the pynput mouse listener."""
        if self.mouse_listener and self.mouse_listener.is_alive():
            logger.info("Arrêt de l'écoute des événements souris.")
            self.mouse_listener.stop()
            self.mouse_listener.join()
            self.mouse_listener = None