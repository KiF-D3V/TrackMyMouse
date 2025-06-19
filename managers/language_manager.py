# managers/language_manager.py

import json
import os
import logging

from utils.paths import get_locales_path
from utils.service_locator import service_locator

# --- MODIFICATION : Logger au niveau du module pour la cohérence ---
logger = logging.getLogger(__name__)

class LanguageManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LanguageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.info("Initialisation de LanguageManager...")
            self.languages = {}
            self.current_language = 'en'
            self.language_codes = ['fr', 'en'] 
            self.unit_codes = ['metric', 'imperial'] 
            self._load_languages()

            # --- AJOUT : Configuration initiale de la langue ---
            try:
                config_manager = service_locator.get_service("config_manager")
                preferred_language = config_manager.get_language()
                self.set_language(preferred_language)
            except Exception as e:
                logger.error(f"Impossible de définir la langue initiale depuis le ConfigManager. Utilisation de '{self.current_language}'. Erreur: {e}")

            self._initialized = True
            logger.info("LanguageManager initialisé.")

    def _load_languages(self):
        logger.debug("Chargement des fichiers de langue...")
        lang_dir = get_locales_path()
        logger.debug(f"Chemin du dossier des langues obtenu depuis utils.paths: {lang_dir}")

        if not os.path.exists(lang_dir) or not os.path.isdir(lang_dir):
            logger.error(f"Le répertoire des langues est introuvable ou n'est pas un dossier à {lang_dir}")
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
                    logger.debug(f"Fichier de langue '{filepath}' chargé et nettoyé pour le code '{lang_code}'.")
                except json.JSONDecodeError:
                    logger.error(f"Erreur de décodage JSON dans le fichier: {filepath}", exc_info=True)
                except Exception as e:
                    logger.error(f"Erreur inattendue lors du chargement du fichier langue {filepath}: {e}", exc_info=True)
        
        if not self.languages:
            logger.warning("Aucun fichier de langue n'a pu être chargé.")
        else:
            logger.info(f"Langues chargées: {', '.join(loaded_langs)}")


    def set_language(self, lang_code: str):
        if lang_code in self.languages:
            if self.current_language != lang_code:
                self.current_language = lang_code
                logger.info(f"Langue changée à: {lang_code}")
            else:
                logger.debug(f"Langue déjà définie à: {lang_code}, pas de changement.")
        else:
            logger.warning(f"Langue '{lang_code}' non disponible. La langue par défaut '{self.current_language}' sera utilisée.")

    def get_text(self, key: str, default_text: str = "") -> str:
        text = self.languages.get(self.current_language, {}).get(key)
        
        if text is None:
            text = self.languages.get('en', {}).get(key)

        if text is None:
            text = default_text
            logger.warning(
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
    
    def get_language_mappings(self) -> tuple[dict, dict]:
        """
        Crée et retourne les dictionnaires de mapping pour les langues.
        
        Returns:
            tuple[dict, dict]: Un tuple contenant (display_to_code, code_to_display).
        """
        display_to_code = {self.get_text(f'language_{code}', code): code for code in self.language_codes}
        code_to_display = {code: name for name, code in display_to_code.items()}
        return display_to_code, code_to_display

    def get_unit_mappings(self) -> tuple[dict, dict]:
        """
        Crée et retourne les dictionnaires de mapping pour les unités.
        
        Returns:
            tuple[dict, dict]: Un tuple contenant (display_to_code, code_to_display).
        """
        display_to_code = {self.get_text(f'unit_{code}', code): code for code in self.unit_codes}
        code_to_display = {code: name for name, code in display_to_code.items()}
        return display_to_code, code_to_display