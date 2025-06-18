# managers/activity_tracker.py

import threading
import time
import datetime
import logging

from utils.event_manager import event_manager
from config.app_config import INACTIVITY_THRESHOLD_SECONDS, ACTIVITY_TRACKER_INTERVAL

# --- MODIFICATION : Logger au niveau du module pour la cohérence ---
logger = logging.getLogger(__name__)

class ActivityTracker(threading.Thread):
    """
    Thread dédié à la surveillance de l'activité/inactivité de l'utilisateur
    et au changement de jour. Il publie des événements pour informer les autres managers.
    """
    def __init__(self):
        super().__init__(daemon=True)
                
        # Dépendances
        self.event_manager = event_manager
        
        # État interne
        self._stop_event = threading.Event()
        self.last_activity_time = time.time()
        self.today = datetime.date.today().isoformat()

        # Le tracker s'abonne lui-même aux événements de la souris pour savoir quand l'utilisateur est actif
        self.event_manager.subscribe('mouse_moved', self._update_last_activity_time)
        self.event_manager.subscribe('mouse_clicked', self._update_last_activity_time)
        logger.info("ActivityTracker initialisé et abonné aux événements de la souris.")

    def _update_last_activity_time(self, *args, **kwargs):
        """Met à jour le temps de la dernière activité détectée."""
        self.last_activity_time = time.time()

    def run(self):
        """
        Boucle principale du thread.
        S'exécute toutes les secondes pour vérifier l'état d'activité et la date.
        """
        logger.info("Le thread du ActivityTracker démarre.")
        while not self._stop_event.is_set():
            # Vérifie le changement de jour
            current_date = datetime.date.today().isoformat()
            if self.today != current_date:
                logger.info(f"Nouveau jour détecté: de {self.today} à {current_date}")
                self.event_manager.publish('day_changed', old_date=self.today, new_date=current_date)
                self.today = current_date
                self._update_last_activity_time() # Réinitialise le timer d'activité

            # Vérifie l'inactivité
            is_inactive = (time.time() - self.last_activity_time) > INACTIVITY_THRESHOLD_SECONDS
            
            if is_inactive:
                self.event_manager.publish('activity_tick', status='inactive')
            else:
                self.event_manager.publish('activity_tick', status='active')

            # Attend l'intervalle défini avant la prochaine vérification
            self._stop_event.wait(ACTIVITY_TRACKER_INTERVAL)
            
        logger.info("Le thread du ActivityTracker s'est arrêté proprement.")

    def stop(self):
        """Signale au thread de s'arrêter."""
        logger.info("Demande d'arrêt du ActivityTracker.")
        self._stop_event.set()