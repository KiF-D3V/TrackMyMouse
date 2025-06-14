# managers/stats_manager.py

import datetime
import logging 
from pynput.mouse import Button
from typing import Optional, List, Dict, Any 

from managers.preference_manager import PreferenceManager
from utils.service_locator import service_locator
from utils.event_manager import event_manager
from .stats_repository import StatsRepository


class StatsManager:
    """
    Gère la logique de suivi des statistiques en temps réel (clics, distance, activité).
    Délègue la persistance et la lecture des données à StatsRepository.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__) 
        self.logger.info("Initialisation de StatsManager...")

        self.stats_repository = StatsRepository()
        service_locator.register_service("stats_repository", self.stats_repository)

        self.preference_manager: PreferenceManager = service_locator.get_service("preference_manager")

        # --- AJOUT : Abonnement aux événements ---
        self.event_manager = event_manager
        self.event_manager.subscribe('mouse_moved', self.update_mouse_position)
        self.event_manager.subscribe('mouse_clicked', self.increment_click)
        self.event_manager.subscribe('activity_tick', self._on_activity_tick)
        self.event_manager.subscribe('day_changed', self._on_day_changed)
        # -----------------------------------------
        
        self.today = datetime.date.today().isoformat()
        self.last_mouse_position: Optional[tuple[int, int]] = None
                        
        self._current_day_stats_in_memory: dict = self._get_or_create_todays_entry()
        self._initialize_app_settings() 
        
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
    
    def increment_click(self, button: Button):
        """Incrémente un clic en mémoire."""
        if button == Button.left: self._current_day_stats_in_memory['left_clicks'] += 1
        elif button == Button.right: self._current_day_stats_in_memory['right_clicks'] += 1
        elif button == Button.middle: self._current_day_stats_in_memory['middle_clicks'] += 1
        
    def _on_activity_tick(self, status: str):
        """
        Met à jour les compteurs de temps d'activité/inactivité
        en réponse à un événement de l'ActivityTracker.
        """
        if status == 'active':
            self._current_day_stats_in_memory['active_time_seconds'] += 1
        elif status == 'inactive':
            self._current_day_stats_in_memory['inactive_time_seconds'] += 1

    def _on_day_changed(self, old_date: str, new_date: str):
        """
        Gère le changement de jour détecté par l'ActivityTracker.
        Sauvegarde les stats de la veille et réinitialise pour le nouveau jour.
        """
        self.logger.info(f"Événement 'day_changed' reçu. Sauvegarde pour {old_date} et réinitialisation pour {new_date}.")
        self.save_changes() 
        self.today = new_date
        self._current_day_stats_in_memory = self._get_or_create_todays_entry()

    def update_mouse_position(self, x: int, y: int):
        """Met à jour la distance en mémoire."""
        if self.last_mouse_position:
            last_x, last_y = self.last_mouse_position
            distance = ((x - last_x)**2 + (y - last_y)**2)**0.5
            self._current_day_stats_in_memory['distance_pixels'] += distance
        self.last_mouse_position = (x, y)
        
    def get_todays_stats(self) -> dict:
        """Retourne les statistiques du jour courant depuis la mémoire."""
        return self._current_day_stats_in_memory

    def get_global_stats(self) -> dict:
        """
        Demande au repository de calculer les statistiques globales et 
        mappe les résultats dans un format attendu par l'application.
        """
        self.logger.debug("Récupération et mappage des statistiques globales.")
        self.save_changes() 
        
        repo_stats = self.stats_repository.get_global_stats()
        
        if not repo_stats:
            return self._get_empty_global_stats_structure()
            
        mapped_stats = {
            'total_distance_pixels': repo_stats.get('total_distance_pixels') or 0.0,
            'left_clicks': repo_stats.get('total_left_clicks') or 0,
            'right_clicks': repo_stats.get('total_right_clicks') or 0,
            'middle_clicks': repo_stats.get('total_middle_clicks') or 0,
            'total_active_time_seconds': repo_stats.get('total_active_time_seconds') or 0,
            'total_inactive_time_seconds': repo_stats.get('total_inactive_time_seconds') or 0,
        }
        return mapped_stats

    def get_first_launch_date(self) -> Optional[str]:
        """Récupère la date de premier lancement via le repository."""
        return self.stats_repository.get_app_setting('first_launch_date')

    def get_last_n_days_stats(self, num_days: int) -> List[Dict[str, Any]]:
        """Récupère l'historique des N derniers jours via le repository."""
        self.save_changes()
        return self.stats_repository.get_last_n_days_stats(num_days)
    
    def get_record_day_for_distance(self) -> Optional[Dict[str, Any]]:
        """
        Demande au repository le jour record pour la distance, après avoir sauvegardé l'état actuel.
        """
        self.logger.debug("Passerelle StatsManager: demande du record de distance.")
        self.save_changes()
        return self.stats_repository.get_record_day_for_distance()

    def get_record_day_for_activity(self) -> Optional[Dict[str, Any]]:
        """
        Demande au repository le jour record pour l'activité, après avoir sauvegardé l'état actuel.
        """
        self.logger.debug("Passerelle StatsManager: demande du record d'activité.")
        self.save_changes()
        return self.stats_repository.get_record_day_for_activity()

    def save_changes(self):
        """Demande au repository de sauvegarder les statistiques en mémoire du jour courant."""
        self.logger.debug("Sauvegarde des changements via le repository.")
        self.stats_repository.update_daily_stats(self._current_day_stats_in_memory)
        self.stats_repository.save_changes()

    def close(self):
        """Arrête le thread, sauvegarde les changements et ferme la connexion du repository."""
        self.logger.info("Demande de fermeture de StatsManager.")
                
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