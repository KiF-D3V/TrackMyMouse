# config/preference_manager.py

import configparser
import os
import screeninfo 
import datetime
from typing import Optional
import appdirs # <--- AJOUT: Import de la bibliothèque appdirs

class PreferenceManager:
    """
    Manages user preferences by reading from and writing to a 'user_preferences.ini' file.
    Implements a singleton pattern to ensure only one instance exists application-wide.
    Handles default preference creation and migration for new settings.
    Stores the INI file in a user-specific configuration directory.
    """
    _instance: Optional['PreferenceManager'] = None
    _initialized: bool = False

    APP_NAME = "TrackMyMouse" # Défini une fois pour l'utiliser avec appdirs

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PreferenceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.config = configparser.ConfigParser()
            self.config_file = 'user_preferences.ini' # Nom du fichier de configuration

            # --- MODIFIÉ : Utilisation d'appdirs pour déterminer le chemin ---
            # Obtenir le dossier de configuration spécifique à l'utilisateur pour cette application
            # Omission de app_author, appdirs utilisera des valeurs par défaut raisonnables ou l'omettra.
            self.app_config_dir = appdirs.user_config_dir(self.APP_NAME)
            
            # Le chemin complet du fichier de configuration sera dans ce dossier utilisateur
            self.full_config_path = os.path.join(self.app_config_dir, self.config_file)
            # L'ancienne variable self.config_dir n'est plus nécessaire de la même manière.
            # --- FIN DE LA MODIFICATION ---
            
            self._ensure_config_file_exists()
            self.load_preferences()
            
            self._initialized = True

    def _ensure_config_file_exists(self):
        """
        Ensures the user-specific configuration directory and file exist.
        Creates the directory and/or the file with default values if necessary.
        Also adds any new default preferences to an existing file.
        """
        # --- MODIFIÉ : Utilisation de self.app_config_dir ---
        # S'assurer que le dossier de configuration utilisateur existe
        if not os.path.exists(self.app_config_dir):
            os.makedirs(self.app_config_dir, exist_ok=True) # exist_ok=True pour ne pas lever d'erreur si le dossier existe déjà
        # --- FIN DE LA MODIFICATION ---

        if not os.path.exists(self.full_config_path):
            self._set_default_preferences()
            self.save_preferences()
        else:
            self.load_preferences() 
            self._add_missing_default_preferences() 
            self.save_preferences() 

    def _generate_first_launch_date_string(self) -> str:
        """
        Generates the first launch date string formatted as AAAA-MM-JJTHH:MM:SS.
        Microseconds are excluded.
        """
        now = datetime.datetime.now()
        return now.replace(microsecond=0).isoformat(timespec='seconds')

    def _set_default_preferences(self):
        """Sets default preferences for a new configuration file."""
        self.config['General'] = {
            'language': 'en',
            'distance_unit': 'metric',
            'first_launch_date': self._generate_first_launch_date_string(),
            'date_format': '%%Y-%%m-%%d %%H:%%M:%%S', 
            'show_first_launch_dialog': 'True',
            'track_mouse_distance': 'True',
            'track_mouse_clicks': 'True'
        }
        self.config['Screen'] = {
            'physical_width_cm': '0.0',
            'physical_height_cm': '0.0',
            'dpi': '96.0', 
            'screen_config_verified': 'False'
        }

    def _add_missing_default_preferences(self):
        """
        Adds any missing default preferences to existing sections
        when an older configuration file is loaded.
        """
        if 'General' not in self.config:
            self.config['General'] = {}
        if 'language' not in self.config['General']:
            self.config['General']['language'] = 'en'
        # ... (les autres vérifications restent les mêmes) ...
        if 'distance_unit' not in self.config['General']:
            self.config['General']['distance_unit'] = 'metric'
        if 'first_launch_date' not in self.config['General']:
            self.config['General']['first_launch_date'] = self._generate_first_launch_date_string()
        if 'date_format' not in self.config['General']:
            self.config['General']['date_format'] = '%%Y-%%m-%%d %%H:%%M:%%S'
        if 'show_first_launch_dialog' not in self.config['General']:
            self.config['General']['show_first_launch_dialog'] = 'True'
        if 'track_mouse_distance' not in self.config['General']:
            self.config['General']['track_mouse_distance'] = 'True'
        if 'track_mouse_clicks' not in self.config['General']:
            self.config['General']['track_mouse_clicks'] = 'True'

        if 'Screen' not in self.config:
            self.config['Screen'] = {}
        if 'physical_width_cm' not in self.config['Screen']:
            self.config['Screen']['physical_width_cm'] = '0.0'
        if 'physical_height_cm' not in self.config['Screen']:
            self.config['Screen']['physical_height_cm'] = '0.0'
        if 'dpi' not in self.config['Screen']:
            self.config['Screen']['dpi'] = '96.0'
        if 'screen_config_verified' not in self.config['Screen']:
            self.config['Screen']['screen_config_verified'] = 'False'


    def load_preferences(self):
        """Loads preferences from the INI file."""
        # Doit gérer le cas où le fichier n'existe pas encore (géré par _ensure_config_file_exists)
        if os.path.exists(self.full_config_path):
            self.config.read(self.full_config_path)
        # else: le fichier sera créé avec les valeurs par défaut par _ensure_config_file_exists

    def save_preferences(self):
        """Saves current preferences to the INI file."""
        # S'assurer que le dossier existe avant de sauvegarder (normalement fait par _ensure_config_file_exists à l'init)
        # Mais une vérification supplémentaire peut être utile si le dossier a été supprimé manuellement.
        if not os.path.exists(self.app_config_dir):
            os.makedirs(self.app_config_dir, exist_ok=True)
        with open(self.full_config_path, 'w') as configfile:
            self.config.write(configfile)

    # --- General Preferences ---
    # Les méthodes get/set pour les préférences spécifiques restent inchangées
    # car elles opèrent sur self.config et self.save_preferences() qui utilisent maintenant
    # les chemins mis à jour.

    def get_language(self) -> str:
        return self.config.get('General', 'language', fallback='en')

    def set_language(self, language: str):
        self.config.set('General', 'language', language)
        self.save_preferences()

    def get_distance_unit(self) -> str:
        return self.config.get('General', 'distance_unit', fallback='metric')

    def set_distance_unit(self, unit: str):
        self.config.set('General', 'distance_unit', unit)
        self.save_preferences()
    
    def get_first_launch_date(self) -> str:
        return self.config.get('General', 'first_launch_date', 
                               fallback=self._generate_first_launch_date_string())

    def set_first_launch_date(self, date_iso_str: str):
        self.config.set('General', 'first_launch_date', date_iso_str)
        self.save_preferences()

    def get_date_format(self) -> str:
        return self.config.get('General', 'date_format', fallback='%%Y-%%m-%%d %%H:%%M:%%S').replace('%%', '%')

    def set_date_format(self, date_format: str):
        self.config.set('General', 'date_format', date_format.replace('%', '%%'))
        self.save_preferences()

    def get_show_first_launch_dialog(self) -> bool:
        return self.config.getboolean('General', 'show_first_launch_dialog', fallback=True)

    def set_show_first_launch_dialog(self, show: bool):
        self.config.set('General', 'show_first_launch_dialog', str(show))
        self.save_preferences()

    def get_track_mouse_distance(self) -> bool:
        return self.config.getboolean('General', 'track_mouse_distance', fallback=True)

    def set_track_mouse_distance(self, track: bool):
        self.config.set('General', 'track_mouse_distance', str(track))
        self.save_preferences()

    def get_track_mouse_clicks(self) -> bool:
        return self.config.getboolean('General', 'track_mouse_clicks', fallback=True)

    def set_track_mouse_clicks(self, track: bool):
        self.config.set('General', 'track_mouse_clicks', str(track))
        self.save_preferences()

    # --- Screen Preferences ---
    def get_physical_width_cm(self) -> float:
        return self.config.getfloat('Screen', 'physical_width_cm', fallback=0.0)

    def get_physical_height_cm(self) -> float:
        return self.config.getfloat('Screen', 'physical_height_cm', fallback=0.0)

    def set_physical_dimensions(self, width: float, height: float, unit: str):
        if unit == 'imperial':
            width_cm = width * 2.54
            height_cm = height * 2.54
        else: 
            width_cm = width
            height_cm = height
        self.config.set('Screen', 'physical_width_cm', str(width_cm))
        self.config.set('Screen', 'physical_height_cm', str(height_cm))
        self.save_preferences()

    def get_dpi(self) -> float:
        return self.config.getfloat('Screen', 'dpi', fallback=96.0)

    def set_dpi(self, dpi: float):
        self.config.set('Screen', 'dpi', str(dpi))
        self.save_preferences()

    def get_screen_config_verified(self) -> bool:
        return self.config.getboolean('Screen', 'screen_config_verified', fallback=False)

    def set_screen_config_verified(self, verified: bool):
        self.config.set('Screen', 'screen_config_verified', str(verified))
        self.save_preferences()

    def calculate_and_set_dpi(self) -> Optional[float]:
        # Cette méthode utilise screeninfo, qui est une dépendance externe.
        # Elle ne dépend pas directement des chemins de fichiers de configuration.
        try:
            monitors = screeninfo.get_monitors()
            if not monitors:
                print("Warning: No monitor detected for DPI calculation.") 
                return None
        except screeninfo.common.ScreenInfoError as e:
            print(f"Warning: Could not get monitor info for DPI calculation: {e}")
            return None


        current_monitor = monitors[0] 
        physical_width_cm = self.get_physical_width_cm()
        physical_height_cm = self.get_physical_height_cm()

        if physical_width_cm > 0 and physical_height_cm > 0:
            physical_width_inches = physical_width_cm / 2.54
            physical_height_inches = physical_height_cm / 2.54
            
            # Assurer que width et height de monitor sont des int pour éviter des erreurs avec getattr
            px_width = current_monitor.width if hasattr(current_monitor, 'width') and isinstance(current_monitor.width, int) else 1920
            px_height = current_monitor.height if hasattr(current_monitor, 'height') and isinstance(current_monitor.height, int) else 1080

            if physical_width_inches == 0 or physical_height_inches == 0: # Éviter la division par zéro
                print("Warning: Physical screen dimensions in inches are zero, cannot calculate DPI.")
                return None

            dpi_x = px_width / physical_width_inches
            dpi_y = px_height / physical_height_inches
            calculated_dpi = (dpi_x + dpi_y) / 2
            self.set_dpi(calculated_dpi)
            return calculated_dpi
        else:
            print("Warning: Physical screen dimensions not defined or invalid for DPI calculation.")
            return None