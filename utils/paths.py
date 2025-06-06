# utils/paths.py

import os
import sys
import appdirs
from typing import Optional

# Nom de l'application et de l'auteur utilisés par appdirs pour créer des chemins standards
# Utiliser un nom d'auteur (même s'il est identique au nom de l'app) est une bonne pratique
# pour une structure de dossier plus claire sur certains OS (ex: AppData\Roaming\AppAuthor\AppName).
APP_NAME = "TrackMyMouse"
APP_AUTHOR = "TrackMyMouse" # Vous pouvez changer ceci si vous le souhaitez

def resource_path(relative_path: str) -> str:
    """
    Obtient le chemin absolu vers une ressource empaquetée avec l'application.
    Fonctionne en mode développement et avec PyInstaller.
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke son chemin dans sys._MEIPASS
        base_path = sys._MEIPASS # type: ignore
    except Exception:
        # En mode développement, on détermine le chemin de base en remontant
        # depuis l'emplacement de ce fichier (utils/) jusqu'à la racine du projet.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    return os.path.join(base_path, relative_path)

def get_user_data_dir() -> str:
    """
    Retourne le chemin du dossier pour les données utilisateur (ex: BDD) et le crée s'il n'existe pas.
    """
    data_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_user_config_dir() -> str:
    """
    Retourne le chemin du dossier pour la configuration utilisateur (ex: .ini) et le crée s'il n'existe pas.
    """
    config_dir = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

# --- Fonctions d'assistance pour obtenir des chemins de fichiers spécifiques ---

def get_db_path() -> str:
    """Retourne le chemin complet et standardisé vers le fichier de la base de données."""
    return os.path.join(get_user_data_dir(), "stats.db")

def get_preferences_path() -> str:
    """Retourne le chemin complet et standardisé vers le fichier de préférences."""
    return os.path.join(get_user_config_dir(), "user_preferences.ini")

def get_locales_path() -> str:
    """Retourne le chemin complet vers le dossier des ressources de langue."""
    return resource_path("locales")

def get_icon_path() -> str:
    """Retourne le chemin complet vers le fichier d'icône principal de l'application."""
    # Assurez-vous que le nom 'systray_icon.ico' est bien celui que vous utilisez
    return resource_path(os.path.join("assets", "icons", "systray_icon.ico"))