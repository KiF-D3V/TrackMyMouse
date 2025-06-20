# core/app_builder.py

import logging
logger = logging.getLogger(__name__)

from core.event_manager import event_manager
from core.service_locator import service_locator

# Import de tous les managers à construire
from managers.config_manager import ConfigManager
from managers.language_manager import LanguageManager
from managers.stats_manager import StatsManager
from managers.activity_tracker import ActivityTracker
from managers.input_manager import InputManager
from modules.level.xp_manager import XPManager

class AppBuilder:
    """
    Construit l'ensemble des services (managers) de l'application,
    gère leurs dépendances et les enregistre dans le service locator.
    """
    def __init__(self):
        self._services = {}

    def build(self) -> dict:
        """
        Orchestre la construction de tous les services et les retourne.
        """
        logger.info("Début de la construction des services de l'application...")

        # L'ordre d'appel est crucial pour gérer les dépendances
        self._build_core_services()
        self._build_managers()
        self._start_background_threads()

        logger.info("Construction des services terminée.")
        return self._services

    def _build_core_services(self):
        """Construit les services fondamentaux comme le ConfigManager."""
        logger.debug("Construction de ConfigManager et LanguageManager...")
        
        config_manager = ConfigManager()
        service_locator.register_service("config_manager", config_manager)
        self._services['config_manager'] = config_manager

        language_manager = LanguageManager()
        service_locator.register_service("language_manager", language_manager)
        self._services['language_manager'] = language_manager

        service_locator.register_service("event_manager", event_manager)
        self._services['event_manager'] = event_manager

    def _build_managers(self):
        """Construit le reste des managers métier."""
        logger.debug("Construction des managers métier...")

        stats_manager = StatsManager()
        service_locator.register_service("stats_manager", stats_manager)
        self._services['stats_manager'] = stats_manager

        xp_manager = XPManager(event_manager=self._services['event_manager'])
        service_locator.register_service("xp_manager", xp_manager)
        self._services['xp_manager'] = xp_manager

        activity_tracker = ActivityTracker()
        self._services['activity_tracker'] = activity_tracker

        input_manager = InputManager()
        service_locator.register_service("input_manager", input_manager)
        self._services['input_manager'] = input_manager

    def _start_background_threads(self):
        """Démarre les services qui tournent en arrière-plan."""
        logger.debug("Démarrage des threads de fond (XPManager, ActivityTracker)...")
        self._services['xp_manager'].start()
        self._services['activity_tracker'].start()
        self._services['input_manager'].start_tracking()