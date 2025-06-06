# config/preference_manager.py

import configparser
import os
import screeninfo 
import datetime
from typing import Optional

# L'import d'appdirs n'est plus nécessaire ici.
# import appdirs 

# --- AJOUT : Import de la nouvelle fonction de gestion de chemin depuis utils.paths ---
from utils.paths import get_preferences_path

class PreferenceManager:
    """
    Gère les préférences utilisateur en lisant et écrivant dans un fichier .ini.
    Le fichier est stocké dans un répertoire de configuration spécifique à l'utilisateur.
    """
    _instance: Optional['PreferenceManager'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PreferenceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.config = configparser.ConfigParser()
            
            # --- MODIFIÉ : Utilisation de la fonction centralisée pour obtenir le chemin ---
            # La logique de construction du chemin est maintenant dans utils/paths.py
            self.full_config_path = get_preferences_path()
            # --- FIN DE LA MODIFICATION ---
            
            self._ensure_config_file_exists()
            self.load_preferences()
            
            self._initialized = True

    def _ensure_config_file_exists(self):
        """
        S'assure que le fichier de configuration existe. Si non, le crée avec les valeurs par défaut.
        Met également à jour les configurations existantes avec les nouvelles clés par défaut si elles sont manquantes.
        """
        # La création du dossier est maintenant gérée par get_preferences_path() dans utils/paths.py
        if not os.path.exists(self.full_config_path):
            self._set_default_preferences()
            self.save_preferences()
        else:
            self.load_preferences() 
            # On vérifie s'il faut ajouter des clés manquantes et on sauvegarde uniquement si nécessaire
            if self._add_missing_default_preferences():
                self.save_preferences()

    def _generate_first_launch_date_string(self) -> str:
        """
        Génère la date du premier lancement au format AAAA-MM-JJTHH:MM:SS.
        """
        now = datetime.datetime.now()
        return now.replace(microsecond=0).isoformat(timespec='seconds')

    def _set_default_preferences(self):
        """Définit les préférences par défaut pour un nouveau fichier de configuration."""
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

    def _add_missing_default_preferences(self) -> bool:
        """
        Ajoute les clés de configuration par défaut manquantes.
        Retourne True si des modifications ont été apportées, False sinon.
        """
        modified = False
        
        if 'General' not in self.config:
            self.config['General'] = {}
            modified = True
        
        # Dictionnaire des clés à vérifier/ajouter pour la section [General]
        general_defaults = {
            'language': 'en',
            'distance_unit': 'metric',
            'first_launch_date': self._generate_first_launch_date_string, # On passe la fonction
            'date_format': '%%Y-%%m-%%d %%H:%%M:%%S',
            'show_first_launch_dialog': 'True',
            'track_mouse_distance': 'True',
            'track_mouse_clicks': 'True'
        }
        for key, value in general_defaults.items():
            if key not in self.config['General']:
                # Si la valeur est une fonction (comme pour la date), on l'appelle pour obtenir la valeur
                self.config['General'][key] = value() if callable(value) else value
                modified = True

        if 'Screen' not in self.config:
            self.config['Screen'] = {}
            modified = True
            
        # Dictionnaire des clés à vérifier/ajouter pour la section [Screen]
        screen_defaults = {
            'physical_width_cm': '0.0',
            'physical_height_cm': '0.0',
            'dpi': '96.0',
            'screen_config_verified': 'False'
        }
        for key, value in screen_defaults.items():
            if key not in self.config['Screen']:
                self.config['Screen'][key] = value
                modified = True
        
        return modified

    def load_preferences(self):
        """Charge les préférences depuis le fichier INI."""
        if os.path.exists(self.full_config_path):
            self.config.read(self.full_config_path)

    def save_preferences(self):
        """Sauvegarde les préférences actuelles dans le fichier INI."""
        with open(self.full_config_path, 'w') as configfile:
            self.config.write(configfile)

    # --- Les méthodes get/set spécifiques restent inchangées ---

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
            
            px_width = current_monitor.width if hasattr(current_monitor, 'width') and isinstance(current_monitor.width, int) else 1920
            px_height = current_monitor.height if hasattr(current_monitor, 'height') and isinstance(current_monitor.height, int) else 1080

            if physical_width_inches == 0 or physical_height_inches == 0:
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