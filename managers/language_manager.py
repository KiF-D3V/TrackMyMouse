# managers/language_manager.py

import json
import os
import sys # Nécessaire pour la fonction resource_path
import logging # Ajout pour le logging
from utils.service_locator import service_locator

# --- COPIE TEMPORAIRE de la fonction resource_path ---
# Idéalement, cette fonction serait dans un module utilitaire partagé (ex: utils.paths)
# et importée ici. Pour l'instant, nous la dupliquons pour avancer sur le packaging.
def resource_path(relative_path: str) -> str:
    """
    Obtient le chemin absolu vers une ressource, fonctionne pour le développement
    et pour les exécutables créés par PyInstaller.
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke son chemin dans _MEIPASS
        base_path = sys._MEIPASS # type: ignore
    except Exception:
        # En développement, _MEIPASS n'est pas défini.
        # On suppose que ce manager est dans un sous-dossier (ex: 'managers')
        # et que les ressources (ex: 'locales') sont à la racine du projet.
        # Chemin du script actuel -> remonter d'un niveau pour être à la racine du projet.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # Si LanguageManager.py était à la racine, ce serait os.path.abspath(".")
        # comme dans main.py. Ajustez si la structure de vos ressources est différente.
        # Pour que resource_path('locales') fonctionne, 'locales' doit être
        # un sous-dossier de base_path.

    return os.path.join(base_path, relative_path)
# --- FIN DE LA COPIE TEMPORAIRE ---

class LanguageManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LanguageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger(__name__) # Ajout du logger
            self.logger.info("Initialisation de LanguageManager...")
            self.languages = {}
            self.current_language = 'en' 
            self._load_languages()
            self._initialized = True
            self.logger.info("LanguageManager initialisé.")


    def _load_languages(self):
        self.logger.debug("Chargement des fichiers de langue...")
        # --- MODIFIÉ : Utilisation de resource_path ---
        # L'ancien calcul de lang_dir basé sur script_dir est remplacé.
        # 'locales' est supposé être un dossier à la racine du projet
        # (ou à la racine de ce que PyInstaller considère comme le dossier de base).
        lang_dir = resource_path('locales')
        self.logger.debug(f"Chemin du dossier des langues déterminé par resource_path: {lang_dir}")
        # --- FIN DE LA MODIFICATION ---

        if not os.path.exists(lang_dir) or not os.path.isdir(lang_dir): # Vérifier aussi si c'est un dossier
            # Remplacer print par un log d'erreur
            self.logger.error(f"Le répertoire des langues est introuvable ou n'est pas un dossier à {lang_dir}")
            return

        loaded_langs = []
        for filename in os.listdir(lang_dir):
            if filename.endswith('.json'):
                lang_code = filename.replace('.json', '')
                filepath = os.path.join(lang_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.languages[lang_code] = json.load(f)
                    loaded_langs.append(lang_code)
                    self.logger.debug(f"Fichier de langue '{filepath}' chargé pour le code '{lang_code}'.")
                except json.JSONDecodeError:
                    self.logger.error(f"Erreur de décodage JSON dans le fichier: {filepath}", exc_info=True)
                except Exception as e:
                    self.logger.error(f"Erreur inattendue lors du chargement du fichier langue {filepath}: {e}", exc_info=True)
        
        if not self.languages:
            self.logger.warning("Aucun fichier de langue n'a pu être chargé.")
        else:
            self.logger.info(f"Langues chargées: {', '.join(loaded_langs)}")


    def set_language(self, lang_code: str):
        if lang_code in self.languages:
            if self.current_language != lang_code:
                self.current_language = lang_code
                self.logger.info(f"Langue changée à: {lang_code}")
            else:
                self.logger.debug(f"Langue déjà définie à: {lang_code}, pas de changement.")
        else:
            # Remplacer print par un log d'avertissement
            self.logger.warning(f"Langue '{lang_code}' non disponible. La langue par défaut '{self.current_language}' sera utilisée.")

    def get_text(self, key: str, default_text: str = "") -> str:
        text = self.languages.get(self.current_language, {}).get(key)
        if text is None:
            # Fallback to English if key not found in current language
            original_default_text = default_text # Garder une trace si le fallback anglais échoue aussi
            text = self.languages.get('en', {}).get(key, default_text)
            if text == original_default_text and key not in self.languages.get('en', {}): # Si toujours le défaut et non trouvé en anglais
                # Remplacer print par un log d'avertissement
                self.logger.warning(f"Clé de texte '{key}' non trouvée dans la langue actuelle ({self.current_language}) ni en anglais. Utilisation du texte par défaut.")
        return text

    def get_current_language(self) -> str:
        return self.current_language

    def get_language_names(self) -> dict:
        """
        Retourne un dictionnaire des noms de langue traduits, mappant les codes (fr, en)
        aux noms d'affichage (Français, English).
        """
        return {
            code: self.get_text(f'language_{code}', code.upper()) # Mettre un fallback plus visible
            for code in self.languages.keys()
        }