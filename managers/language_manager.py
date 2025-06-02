# managers/language_manager.py

import json
import os
from utils.service_locator import service_locator

class LanguageManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LanguageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.languages = {}
            self.current_language = 'en' # Langue par défaut avant chargement des préférences
            # La langue sera configurée par main.py après que tous les services soient enregistrés
            # et que PreferenceManager soit accessible.
            self._load_languages() # Appelé ici pour s'assurer que les langues sont chargées au moment de l'initialisation.
            self._initialized = True


    def _load_languages(self):
        script_dir = os.path.dirname(__file__)
        # ANCIEN CHEMIN: lang_dir = os.path.join(script_dir, '..', '..', 'locales')
        # CORRECTION : Remonte un seul niveau (de managers/ à mouse_tracker/), puis descend dans 'locales'
        lang_dir = os.path.join(script_dir, '..', 'locales') 

        if not os.path.exists(lang_dir):
            print(f"Erreur: Le répertoire des langues est introuvable à {lang_dir}")
            # Vous pourriez vouloir lever une exception ou gérer cela de manière plus robuste
            return

        for filename in os.listdir(lang_dir):
            if filename.endswith('.json'):
                lang_code = filename.replace('.json', '')
                filepath = os.path.join(lang_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.languages[lang_code] = json.load(f)

    def set_language(self, lang_code: str):
        if lang_code in self.languages:
            self.current_language = lang_code
        else:
            print(f"Langue '{lang_code}' non disponible. La langue par défaut '{self.current_language}' sera utilisée.")

    def get_text(self, key: str, default_text: str = "") -> str:
        text = self.languages.get(self.current_language, {}).get(key)
        if text is None:
            # Fallback to English if key not found in current language
            text = self.languages.get('en', {}).get(key, default_text)
            if text == default_text:
                print(f"Attention: Clé de texte '{key}' non trouvée dans la langue actuelle ({self.current_language}) ni en anglais. Utilisation du texte par défaut.")
        return text

    def get_current_language(self) -> str:
        return self.current_language

    def get_language_names(self) -> dict:
        """
        Retourne un dictionnaire des noms de langue traduits, mappant les codes (fr, en)
        aux noms d'affichage (Français, English).
        """
        return {
            code: self.get_text(f'language_{code}', code)
            for code in self.languages.keys()
        }