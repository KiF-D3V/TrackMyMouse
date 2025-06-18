# managers/preference_manager.py

import configparser
import os
import screeninfo 
import datetime
import logging
from typing import Optional
from utils.paths import get_preferences_path
from config.app_config import OPTIONAL_TABS

# --- AJOUT : Logger au niveau du module ---
logger = logging.getLogger(__name__)

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
            logger.info("Initialisation de PreferenceManager...")
            self.config = configparser.ConfigParser()
            self.full_config_path = get_preferences_path()
            self._ensure_config_file_exists()
            self.load_preferences()
            self._initialized = True
            logger.info("PreferenceManager initialisé.")

    def _ensure_config_file_exists(self):
        """
        S'assure que le fichier de configuration existe. Si non, le crée avec les valeurs par défaut.
        Met également à jour les configurations existantes avec les nouvelles clés par défaut si elles sont manquantes.
        """
        if not os.path.exists(self.full_config_path):
            logger.info(f"Fichier de configuration introuvable. Création d'un nouveau fichier à : {self.full_config_path}")
            self._set_default_preferences()
            self.save_preferences()
        else:
            self.load_preferences() 
            if self._add_missing_default_preferences():
                logger.info("Préférences par défaut manquantes ajoutées au fichier de configuration.")
                self.save_preferences()

    def _generate_first_launch_date_string(self) -> str:
        """Génère la date du premier lancement au format AAAA-MM-JJTHH:MM:SS."""
        return datetime.datetime.now().replace(microsecond=0).isoformat(timespec='seconds')

    def _set_default_preferences(self):
        """Définit les préférences par défaut pour un nouveau fichier de configuration."""
        logger.debug("Définition des préférences par défaut.")
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
        # --- AJOUT: Nouvelle section pour les fonctionnalités ---
        self.config['Features'] = {}
        for tab_info in OPTIONAL_TABS:
            preference_key = tab_info["preference_key"]
            # On met 'True' comme valeur par défaut pour tous les onglets
            self.config['Features'][preference_key] = 'True'

    def _add_missing_default_preferences(self) -> bool:
        """
        Ajoute les clés de configuration par défaut manquantes.
        Retourne True si des modifications ont été apportées, False sinon.
        """
        modified = False
        
        # Section [General]
        if 'General' not in self.config:
            self.config['General'] = {}
            modified = True
        general_defaults = {
            'language': 'en', 'distance_unit': 'metric',
            'first_launch_date': self._generate_first_launch_date_string,
            'date_format': '%%Y-%%m-%%d %%H:%%M:%%S',
            'show_first_launch_dialog': 'True', 'track_mouse_distance': 'True',
            'track_mouse_clicks': 'True'
        }
        for key, value in general_defaults.items():
            if key not in self.config['General']:
                self.config['General'][key] = value() if callable(value) else value
                modified = True

        # Section [Screen]
        if 'Screen' not in self.config:
            self.config['Screen'] = {}
            modified = True
        screen_defaults = {
            'physical_width_cm': '0.0', 'physical_height_cm': '0.0',
            'dpi': '96.0', 'screen_config_verified': 'False'
        }
        for key, value in screen_defaults.items():
            if key not in self.config['Screen']:
                self.config['Screen'][key] = value
                modified = True

        # SECTION [Features]
        if 'Features' not in self.config:
            self.config['Features'] = {}
            modified = True
        
        # On parcourt le registre OPTIONAL_TABS pour ajouter les clés dynamiquement
        for tab_info in OPTIONAL_TABS:
            preference_key = tab_info["preference_key"]
            if preference_key not in self.config['Features']:
                # On met 'True' comme valeur par défaut pour tous les onglets optionnels
                self.config['Features'][preference_key] = 'True'
                modified = True
        
        return modified
    

    def load_preferences(self):
        """Charge les préférences depuis le fichier INI."""
        if os.path.exists(self.full_config_path):
            logger.debug(f"Chargement des préférences depuis {self.full_config_path}")
            self.config.read(self.full_config_path)

    def save_preferences(self):
        """Sauvegarde les préférences actuelles dans le fichier INI."""
        logger.debug(f"Sauvegarde des préférences dans {self.full_config_path}")
        with open(self.full_config_path, 'w') as configfile:
            self.config.write(configfile)

    # --- Getters/Setters pour [General] ---
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
        return self.config.get('General', 'first_launch_date', fallback=self._generate_first_launch_date_string())

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

    # --- Getters/Setters pour [Screen] ---
    def get_physical_width_cm(self) -> float:
        return self.config.getfloat('Screen', 'physical_width_cm', fallback=0.0)

    def get_physical_height_cm(self) -> float:
        return self.config.getfloat('Screen', 'physical_height_cm', fallback=0.0)

    def set_physical_dimensions(self, width: float, height: float, unit: str):
        if unit == 'imperial':
            width_cm, height_cm = width * 2.54, height * 2.54
        else: 
            width_cm, height_cm = width, height
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

    # Getters/Setters pour la nouvelle section [Features]

    def get_show_tab(self, tab_id: str) -> bool:
        # On cherche la configuration de l'onglet dans notre registre central
        for tab_info in OPTIONAL_TABS:
            if tab_info["id"] == tab_id:
                preference_key = tab_info["preference_key"]
                return self.config.getboolean('Features', preference_key, fallback=True)
        # Si l'ID n'est pas trouvé dans le registre, on n'affiche pas par sécurité
        return False
    
    def set_show_tab(self, tab_id: str, value: bool):
        # On cherche la configuration de l'onglet dans notre registre central
        for tab_info in OPTIONAL_TABS:
            if tab_info["id"] == tab_id:
                preference_key = tab_info["preference_key"]
                self.config.set('Features', preference_key, str(value))
                self.save_preferences()
                # On peut sortir de la boucle une fois la clé trouvée et modifiée
                return


    def calculate_and_set_dpi(self) -> Optional[float]:
        try:
            monitors = screeninfo.get_monitors()
            if not monitors:
                logger.warning("Aucun moniteur détecté pour le calcul du DPI.")
                return None
        except screeninfo.common.ScreenInfoError as e:
            logger.warning(f"Impossible d'obtenir les informations du moniteur pour le calcul du DPI : {e}")
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
                logger.warning("Les dimensions physiques de l'écran en pouces sont nulles, impossible de calculer le DPI.")
                return None

            dpi_x = px_width / physical_width_inches
            dpi_y = px_height / physical_height_inches
            calculated_dpi = (dpi_x + dpi_y) / 2
            logger.info(f"DPI calculé avec succès : {calculated_dpi:.2f}")
            self.set_dpi(calculated_dpi)
            return calculated_dpi
        else:
            logger.warning("Dimensions physiques de l'écran non définies ou invalides pour le calcul du DPI.")
            return None