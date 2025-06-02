# managers/input_manager.py

from pynput import mouse
import threading
from utils.service_locator import service_locator

class InputManager:
    """
    Manages global mouse input events (movements and clicks) using pynput.
    It dispatches these events to the StatsManager based on user preferences.
    """
    def __init__(self):
        self.mouse_listener = None
        self.stats_manager = service_locator.get_service("stats_manager")
        self.preference_manager = service_locator.get_service("preference_manager")

        # Basic check for manager availability. In a production app, robust logging would be used.
        if not self.stats_manager:
            print("Error: StatsManager not available for InputManager. Mouse tracking will not function.")
        if not self.preference_manager:
            print("Error: PreferenceManager not available for InputManager. Mouse tracking will not function.")

    def _on_move(self, x, y):
        """
        Callback function for mouse movement events.
        Updates mouse position in StatsManager if distance tracking is enabled.
        """
        if self.preference_manager and self.preference_manager.get_track_mouse_distance():
            self.stats_manager.update_mouse_position(x, y)

    def _on_click(self, x, y, button, pressed):
        """
        Callback function for mouse click events.
        Increments click count in StatsManager if click tracking is enabled and button is pressed.
        """
        # Only process on button press, not release
        if pressed and self.preference_manager and self.preference_manager.get_track_mouse_clicks():
            self.stats_manager.increment_click(button)

    def start_tracking(self):
        """
        Starts the pynput mouse listener in a separate thread.
        Ensures only one listener is active at a time.
        """
        if self.mouse_listener is None or not self.mouse_listener.is_alive():
            # A single listener for all mouse events
            self.mouse_listener = mouse.Listener(
                on_move=self._on_move,
                on_click=self._on_click
            )
            self.mouse_listener.start()
        # else: print("InputManager: Mouse tracking is already running.") # Supprimé, pas besoin de message si déjà démarré

    def stop_tracking(self):
        """
        Stops the pynput mouse listener and waits for its thread to terminate.
        Ensures a clean shutdown of the tracking process.
        """
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
            self.mouse_listener.join() # Wait for the listener thread to finish
            self.mouse_listener = None
        # else: print("InputManager: Mouse tracking is not active or already stopped.") # Supprimé, pas besoin de message si déjà arrêté