# core/event_manager.py

import logging
from collections import defaultdict
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventManager:
    """
    Gestionnaire d'événements Singleton pour une architecture Publish/Subscribe.
    Permet un couplage faible entre les différents composants de l'application.
    """
    _instance = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Un dictionnaire pour stocker les abonnés à chaque événement.
            # defaultdict(list) crée automatiquement une liste vide pour les nouveaux événements.
            self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
            self._initialized = True

    def subscribe(self, event_name: str, callback: Callable):
        """
        Abonne une fonction (callback) à un événement.
        """
        self.subscribers[event_name].append(callback)

    def publish(self, event_name: str, *args: Any, **kwargs: Any):
        """
        Publie un événement, ce qui déclenche tous les callbacks abonnés.
        """
        if event_name in self.subscribers:
            # Appelle chaque fonction abonnée avec les arguments fournis
            for callback in self.subscribers[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    # Log l'erreur mais continue d'appeler les autres abonnés
                    # exc_info=True inclut automatiquement les détails de l'erreur dans le log
                    logger.error(
                        f"Erreur lors de l'appel du callback '{callback.__name__}' pour l'événement '{event_name}'", 
                        exc_info=True
                    )

# Instance unique du gestionnaire d'événements pour toute l'application
event_manager = EventManager()