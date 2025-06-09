# managers/language_manager.py

import json
import os
import sys 
import logging
from utils.service_locator import service_locator

from utils.paths import get_locales_path

class LanguageManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LanguageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger(__name__) 
            self.logger.info("Initialisation de LanguageManager...")
            self.languages = {}
            self.current_language = 'en' 
            self._load_languages()
            self._initialized = True
            self.logger.info("LanguageManager initialisé.")


    # --- MÉTHODE CORRIGÉE (VERSION FINALE) ---
    def _load_languages(self):
        self.logger.debug("Chargement des fichiers de langue...")
        lang_dir = get_locales_path()
        self.logger.debug(f"Chemin du dossier des langues obtenu depuis utils.paths: {lang_dir}")

        if not os.path.exists(lang_dir) or not os.path.isdir(lang_dir):
            self.logger.error(f"Le répertoire des langues est introuvable ou n'est pas un dossier à {lang_dir}")
            return

        # Caractères à supprimer : tous les espaces standards + l'espace insécable
        WHITESPACE_CHARS_TO_STRIP = ' \t\n\r\f\v\u00A0'

        loaded_langs = []
        for filename in os.listdir(lang_dir):
            if filename.endswith('.json'):
                lang_code = filename.replace('.json', '')
                filepath = os.path.join(lang_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # On nettoie chaque clé avec la liste complète des caractères d'espacement
                        self.languages[lang_code] = {k.strip(WHITESPACE_CHARS_TO_STRIP): v for k, v in data.items()}
                    loaded_langs.append(lang_code)
                    self.logger.debug(f"Fichier de langue '{filepath}' chargé et nettoyé pour le code '{lang_code}'.")
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
            self.logger.warning(f"Langue '{lang_code}' non disponible. La langue par défaut '{self.current_language}' sera utilisée.")

    def get_text(self, key: str, default_text: str = "") -> str:
        text = self.languages.get(self.current_language, {}).get(key)
        
        if text is None:
            text = self.languages.get('en', {}).get(key)

        if text is None:
            text = default_text
            self.logger.warning(
                f"Clé de texte '{key}' non trouvée dans la langue actuelle "
                f"({self.current_language}) ni en anglais. Utilisation du texte par défaut."
            )
            
        return text

    def get_current_language(self) -> str:
        return self.current_language

    def get_language_names(self) -> dict:
        return {
            code: self.get_text(f'language_{code}', code.upper()) 
            for code in self.languages.keys()
        }