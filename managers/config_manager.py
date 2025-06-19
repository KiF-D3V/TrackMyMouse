# managers/config_manager.py

import logging
from typing import Any, Optional

import config.app_config as app_config
from managers.preference_manager import PreferenceManager

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manager Singleton agissant comme source de vérité unique pour toute la configuration.
    Il fournit un accès unifié aux constantes de l'application (app_config.py)
    et aux préférences de l'utilisateur (user_preferences.ini via PreferenceManager).
    """
    _instance: Optional['ConfigManager'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.info("Initialisation de ConfigManager...")
            
            self._static_config = {
                key: getattr(app_config, key)
                for key in dir(app_config)
                if key.isupper() and not key.startswith('_')
            }
            logger.debug(f"Configuration statique chargée : {list(self._static_config.keys())}")

            self._pref_manager = PreferenceManager()
            
            self._initialized = True
            logger.info("ConfigManager initialisé.")

    # --- Accès à la configuration statique (app_config.py) ---

    def get_app_config(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur depuis la configuration statique de l'application."""
        return self._static_config.get(key, default)

    # --- Façade complète pour les méthodes de PreferenceManager ---

    def save_preferences(self):
        """Sauvegarde les préférences via PreferenceManager."""
        self._pref_manager.save_preferences()
        
    def calculate_and_set_dpi(self) -> Optional[float]:
        """Calcule et sauvegarde le DPI via PreferenceManager."""
        return self._pref_manager.calculate_and_set_dpi()

    # --- Méthodes "General" ---
    def get_language(self) -> str: return self._pref_manager.get_language()
    def set_language(self, language: str): self._pref_manager.set_language(language)

    def get_distance_unit(self) -> str: return self._pref_manager.get_distance_unit()
    def set_distance_unit(self, unit: str): self._pref_manager.set_distance_unit(unit)
    
    def get_first_launch_date(self) -> str: return self._pref_manager.get_first_launch_date()
    def set_first_launch_date(self, date_iso_str: str): self._pref_manager.set_first_launch_date(date_iso_str)
    
    def get_date_format(self) -> str: return self._pref_manager.get_date_format()
    def set_date_format(self, date_format: str): self._pref_manager.set_date_format(date_format)

    def get_show_first_launch_dialog(self) -> bool: return self._pref_manager.get_show_first_launch_dialog()
    def set_show_first_launch_dialog(self, show: bool): self._pref_manager.set_show_first_launch_dialog(show)

    def get_track_mouse_distance(self) -> bool: return self._pref_manager.get_track_mouse_distance()
    def set_track_mouse_distance(self, track: bool): self._pref_manager.set_track_mouse_distance(track)

    def get_track_mouse_clicks(self) -> bool: return self._pref_manager.get_track_mouse_clicks()
    def set_track_mouse_clicks(self, track: bool): self._pref_manager.set_track_mouse_clicks(track)

    # --- Méthodes "Screen" ---
    def get_physical_width_cm(self) -> float: return self._pref_manager.get_physical_width_cm()
    def get_physical_height_cm(self) -> float: return self._pref_manager.get_physical_height_cm()
    def set_physical_dimensions(self, width: float, height: float, unit: str): self._pref_manager.set_physical_dimensions(width, height, unit)
    
    def get_dpi(self) -> float: return self._pref_manager.get_dpi()
    def set_dpi(self, dpi: float): self._pref_manager.set_dpi(dpi)
    
    def get_screen_config_verified(self) -> bool: return self._pref_manager.get_screen_config_verified()
    def set_screen_config_verified(self, verified: bool): self._pref_manager.set_screen_config_verified(verified)

    # --- Méthodes "Features" ---
    def get_show_tab(self, tab_id: str) -> bool: return self._pref_manager.get_show_tab(tab_id)
    def set_show_tab(self, tab_id: str, value: bool): self._pref_manager.set_show_tab(tab_id, value)