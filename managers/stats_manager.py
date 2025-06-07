# managers/stats_manager.py

import datetime
import time
import threading 
import logging 
from pynput import mouse # type: ignore
from typing import Optional, List, Dict, Any 

from managers.preference_manager import PreferenceManager
from utils.service_locator import service_locator
# --- AJOUT : Import du nouveau StatsRepository ---
from .stats_repository import StatsRepository


# --- Constants ---
INACTIVITY_THRESHOLD_SECONDS = 2 

class StatsManager:
    """
    Gère la logique de suivi des statistiques en temps réel (clics, distance, activité).
    Délègue la persistance et la lecture des données à StatsRepository.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__) 
        self.logger.info("Initialisation de StatsManager...")

        # --- MODIFIÉ : Utilisation de StatsRepository ---
        self.stats_repository = StatsRepository()
        service_locator.register_service("stats_repository", self.stats_repository)
        # --- FIN DE LA MODIFICATION ---

        self.preference_manager: PreferenceManager = service_locator.get_service("preference_manager")
        
        self.today = datetime.date.today().isoformat()
        self.last_mouse_position: Optional[tuple[int, int]] = None
        self.last_activity_time: float = time.time()
        self.is_active: bool = True 
        self._stop_tracker: bool = False
        
        self._current_day_stats_in_memory: dict = self._get_or_create_todays_entry()
        self._initialize_app_settings() 

        self._activity_tracker_thread = threading.Thread(target=self._run_activity_tracker, daemon=True)
        self._activity_tracker_thread.start()
        self.logger.info("StatsManager initialisé et tracker d'activité démarré.")

    def _initialize_app_settings(self):
        """
        S'assure que 'first_launch_date' est en BDD via le repository.
        """
        if self.stats_repository.get_app_setting('first_launch_date') is None:
            self.logger.info("'first_launch_date' non trouvée. Lecture depuis PreferenceManager.")
            try:
                first_launch_date_str = self.preference_manager.get_first_launch_date()
                self.stats_repository.set_app_setting('first_launch_date', first_launch_date_str)
            except Exception as e:
                self.logger.error(f"Erreur lors de l'initialisation de 'first_launch_date': {e}", exc_info=True)
        else:
            self.logger.debug("'first_launch_date' déjà présente dans la BDD.")

    def _get_or_create_todays_entry(self) -> dict:
        """
        Récupère ou crée les stats du jour via le repository.
        """
        todays_stats = self.stats_repository.get_daily_stats(self.today)
        if todays_stats is None:
            self.logger.info(f"Aucune entrée pour {self.today}, création via le repository.")
            self.stats_repository.create_daily_stats_entry(self.today)
            todays_stats = self.stats_repository.get_daily_stats(self.today)
        
        return todays_stats if todays_stats else self._get_initial_daily_stats_structure()

    def _run_activity_tracker(self):
        """
        Thread qui gère le temps d'activité/inactivité et le changement de jour.
        """
        self.logger.info("Thread de suivi d'activité démarré.")
        while not self._stop_tracker:
            time.sleep(1) 
            if self._stop_tracker: break

            current_date = datetime.date.today().isoformat()
            if self.today != current_date:
                self.logger.info(f"Nouveau jour détecté: {current_date}.")
                self.save_changes() 
                self.today = current_date
                self._current_day_stats_in_memory = self._get_or_create_todays_entry()
                self.last_activity_time = time.time() 
                self.is_active = True 
                self.logger.info(f"Statistiques réinitialisées pour le nouveau jour: {self.today}.")

            if (time.time() - self.last_activity_time) <= INACTIVITY_THRESHOLD_SECONDS:
                if not self.is_active: self.is_active = True
                self._current_day_stats_in_memory['active_time_seconds'] += 1
            else:
                if self.is_active: self.is_active = False
                self._current_day_stats_in_memory['inactive_time_seconds'] += 1
        self.logger.info("Thread de suivi d'activité terminé.")

    def increment_click(self, button: mouse.Button):
        """Incrémente un clic en mémoire."""
        if button == mouse.Button.left: self._current_day_stats_in_memory['left_clicks'] += 1
        elif button == mouse.Button.right: self._current_day_stats_in_memory['right_clicks'] += 1
        elif button == mouse.Button.middle: self._current_day_stats_in_memory['middle_clicks'] += 1
        self.last_activity_time = time.time()
        if not self.is_active: self.is_active = True

    def update_mouse_position(self, x: int, y: int):
        """Met à jour la distance en mémoire."""
        if self.last_mouse_position:
            last_x, last_y = self.last_mouse_position
            distance = ((x - last_x)**2 + (y - last_y)**2)**0.5
            self._current_day_stats_in_memory['distance_pixels'] += distance
        self.last_mouse_position = (x, y)
        self.last_activity_time = time.time() 
        if not self.is_active: self.is_active = True 

    def get_todays_stats(self) -> dict:
        """Retourne les statistiques du jour courant depuis la mémoire."""
        return self._current_day_stats_in_memory

    def get_global_stats(self) -> dict:
        """Demande au repository de calculer les statistiques globales."""
        self.logger.debug("Récupération des statistiques globales via le repository.")
        self.save_changes() 
        global_stats = self.stats_repository.get_global_stats()
        return global_stats if global_stats else self._get_empty_global_stats_structure()

    def get_first_launch_date(self) -> Optional[str]:
        """Récupère la date de premier lancement via le repository."""
        return self.stats_repository.get_app_setting('first_launch_date')

    def get_last_n_days_stats(self, num_days: int) -> List[Dict[str, Any]]:
        """Récupère l'historique des N derniers jours via le repository."""
        self.save_changes()
        return self.stats_repository.get_last_n_days_stats(num_days)

    def save_changes(self):
        """Demande au repository de sauvegarder les statistiques en mémoire du jour courant."""
        self.logger.debug("Sauvegarde des changements via le repository.")
        self.stats_repository.update_daily_stats(self._current_day_stats_in_memory)
        self.stats_repository.save_changes()

    def close(self):
        """Arrête le thread, sauvegarde les changements et ferme la connexion du repository."""
        self.logger.info("Demande de fermeture de StatsManager.")
        self._stop_tracker = True 
        if self._activity_tracker_thread and self._activity_tracker_thread.is_alive():
            self.logger.info("Attente de la terminaison du thread de suivi d'activité...") 
            self._activity_tracker_thread.join(timeout=2.0) 
            self.logger.info("Thread de suivi d'activité terminé.")
        
        self.logger.info("Sauvegarde finale des changements avant fermeture.")
        self.save_changes() 
        self.stats_repository.close()
        self.logger.info("StatsManager et son repository sont fermés.")

    def _get_initial_daily_stats_structure(self) -> dict:
        """Retourne un dictionnaire représentant l'état initial des statistiques journalières."""
        return {
            'date': self.today, 'distance_pixels': 0.0, 'left_clicks': 0, 'right_clicks': 0,
            'middle_clicks': 0, 'active_time_seconds': 0, 'inactive_time_seconds': 0
        }

    def _get_empty_global_stats_structure(self) -> dict:
        """Retourne une structure vide pour les statistiques globales en cas d'erreur."""
        return {
            'total_distance_pixels': 0.0, 'left_clicks': 0, 'right_clicks': 0, 
            'middle_clicks': 0, 'total_active_time_seconds': 0, 'total_inactive_time_seconds': 0
        }