# managers/input_manager.py

# --- MODIFIÉ : Import plus spécifique et ajout de l'EventManager ---
from pynput.mouse import Listener, Button
from utils.event_manager import event_manager
from utils.service_locator import service_locator

class InputManager:
    """
    Manages global mouse input events (movements and clicks) using pynput.
    It publishes these events using the EventManager.
    """
    def __init__(self):
        self.mouse_listener = None
        
        # --- MODIFIÉ : On remplace la dépendance à StatsManager par EventManager ---
        self.event_manager = event_manager
        self.preference_manager = service_locator.get_service("preference_manager")

        if not self.preference_manager:
            print("Error: PreferenceManager not available for InputManager.")

    def _on_move(self, x, y):
        """
        Callback for mouse movement events. Publishes a 'mouse_moved' event.
        """
        if self.preference_manager and self.preference_manager.get_track_mouse_distance():
            # --- MODIFIÉ : On publie un événement au lieu d'appeler un manager ---
            self.event_manager.publish('mouse_moved', x=x, y=y)

    def _on_click(self, x, y, button: Button, pressed: bool):
        """
        Callback for mouse click events. Publishes a 'mouse_clicked' event on press.
        """
        if pressed and self.preference_manager and self.preference_manager.get_track_mouse_clicks():
            # --- MODIFIÉ : On publie un événement au lieu d'appeler un manager ---
            self.event_manager.publish('mouse_clicked', button=button)

    def start_tracking(self):
        """
        Starts the pynput mouse listener in a separate thread.
        """
        if self.mouse_listener is None or not self.mouse_listener.is_alive():
            self.mouse_listener = Listener(
                on_move=self._on_move,
                on_click=self._on_click
            )
            self.mouse_listener.start()

    def stop_tracking(self):
        """
        Stops the pynput mouse listener.
        """
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
            self.mouse_listener.join()
            self.mouse_listener = None