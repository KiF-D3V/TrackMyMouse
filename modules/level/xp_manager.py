# modules/level/xp_manager.py

import os
import json
import logging
from threading import Timer
from typing import Optional
from pynput.mouse import Button

from utils.paths import resource_path
from utils.math_utils import calculate_distance
from modules.level.xp_repository import XPRepository
from core.service_locator import service_locator

logger = logging.getLogger(__name__)

class XPManager:
    """
    Gère toute la logique de gain d'XP et de calcul des niveaux.
    """
    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._repository = XPRepository()
        self.config_manager = service_locator.get_service("config_manager")
        self._load_config()
        
        # Attributs pour le suivi en temps réel
        self.total_points = self._repository.get_total_points()
        self.current_level = 0
        self.accumulated_pixels = 0.0
        self.last_x: Optional[int] = None
        self.last_y: Optional[int] = None
        
        self._save_timer = None

        # Initialisation du niveau de départ
        self._initialize_level()

    def _load_config(self):
        """Charge la configuration depuis xp_config.json."""
        relative_path_to_config = os.path.join("modules", "level", "xp_config.json")
        config_path = resource_path(relative_path_to_config)
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def start(self):
        """Démarre le manager : s'abonne aux événements et lance le timer de sauvegarde."""
        self._event_manager.subscribe('mouse_moved', self._on_mouse_moved)
        self._event_manager.subscribe('mouse_clicked', self._on_mouse_clicked)
        self._event_manager.subscribe('activity_tick', self._on_activity_tick)
        
        self._schedule_next_save()
        logger.info("XPManager démarré.")

    def stop(self):
        """Arrête le manager : sauvegarde finale et arrêt du timer."""
        if self._save_timer:
            self._save_timer.cancel()
        self.save_progress()
        self._repository.close()
        logger.info("XPManager arrêté.")

    def save_progress(self):
        """Sauvegarde la progression actuelle dans la base de données."""
        self._repository.save_total_points(self.total_points)

    def _schedule_next_save(self):
        """Planifie la prochaine sauvegarde automatique."""
        save_interval = self.config_manager.get_app_config('XP_SAVE_INTERVAL_SECONDS', 3600)
        self._save_timer = Timer(save_interval, self._periodic_save)
        self._save_timer.daemon = True
        self._save_timer.start()

    def _periodic_save(self):
        """Méthode appelée par le timer pour sauvegarder périodiquement."""
        self.save_progress()
        self._schedule_next_save()

    # --- Logique de gain de points ---

    def _on_mouse_moved(self, x: int, y: int, **kwargs):
        """Appelée par l'EventManager lorsque la souris bouge."""
        if self.last_x is not None and self.last_y is not None:
            distance = calculate_distance((self.last_x, self.last_y), (x, y))
            self.accumulated_pixels += distance
        
        self.last_x, self.last_y = x, y

        # On lit le seuil depuis le fichier de configuration.
        pixel_award_threshold = self.config.get("pixel_award_threshold", 1000)

        if self.accumulated_pixels >= pixel_award_threshold:
            points_to_add = int(self.accumulated_pixels) * self.config['xp_gain_rates_scaled']['per_pixel']
            self.total_points += points_to_add
            self.accumulated_pixels = 0.0

            logger.debug(f"Mouvement: +{points_to_add} points. Total = {self.total_points}")
            
            self._check_for_level_up()

    def _on_mouse_clicked(self, button: Button, **kwargs):
        """Appelée par l'EventManager lors d'un clic de souris."""
        button_to_config_key = {
            Button.left: 'per_left_click',
            Button.right: 'per_right_click',
            Button.middle: 'per_middle_click'
        }
        config_key = button_to_config_key.get(button)
        
        if config_key:
            points_to_add = self.config['xp_gain_rates_scaled'].get(config_key, 0)
            self.total_points += points_to_add
                        
            logger.debug(f"Clic '{button.name}': +{points_to_add} points. Total = {self.total_points}")

            self._check_for_level_up()

    def _on_activity_tick(self, status: str, **kwargs):
        """Appelée par l'EventManager chaque seconde d'activité."""
        if status == 'active':
            points_to_add = self.config['xp_gain_rates_scaled']['per_active_second']
            self.total_points += points_to_add
            self._check_for_level_up()
    
    # --- Logique de calcul de niveau ---

    def _get_cumulative_xp_for_level(self, level: int) -> float:
        """Outil interne pour calculer le total d'XP requis pour atteindre un niveau donné."""
        if level <= 1:
            return 0
        
        base_xp = self.config['leveling_formula']['base_xp']
        exponent = self.config['leveling_formula']['exponent']
        
        total_xp_needed = 0
        for i in range(1, level):
            total_xp_needed += base_xp * (i ** exponent)
        return total_xp_needed

    def get_level_details(self) -> dict:
        """
        Calcule et retourne un dictionnaire contenant tous les détails
        nécessaires à l'affichage de la progression de l'utilisateur.
        C'est la méthode publique que l'interface (LevelTab) appellera.
        """
        # Conversion des points en XP
        scaling_factor = self.config.get("xp_unit_scaling_factor", 10000)
        current_xp = self.total_points / scaling_factor
        
        # Détermination du niveau actuel
        level = self._get_level_from_points(self.total_points)

        # Calcul des seuils d'XP pour le niveau actuel et le suivant
        xp_start_of_current_level = self._get_cumulative_xp_for_level(level)
        xp_to_reach_next_level = self._get_cumulative_xp_for_level(level + 1)
        
        # Calcul de la progression dans le niveau actuel
        xp_span_for_this_level = xp_to_reach_next_level - xp_start_of_current_level
        xp_in_current_level = current_xp - xp_start_of_current_level
        
        progress_percentage = (xp_in_current_level / xp_span_for_this_level) * 100 if xp_span_for_this_level > 0 else 0

        return {
            "current_level": level,
            "current_xp_str": f"{xp_in_current_level:,.0f} / {xp_span_for_this_level:,.0f} XP",
            "progress_percentage": progress_percentage
        }

    def _get_level_from_points(self, points: int) -> int:
        """Calcule le niveau correspondant à un certain nombre de points."""
        scaling_factor = self.config.get("xp_unit_scaling_factor", 10000)
        current_xp = points / scaling_factor

        base_xp = self.config['leveling_formula']['base_xp']
        exponent = self.config['leveling_formula']['exponent']
        
        level = 1
        total_xp_for_level_up = 0
        while True:
            xp_to_reach_next_level = base_xp * (level ** exponent)
            total_xp_for_level_up += xp_to_reach_next_level
            
            if current_xp < total_xp_for_level_up:
                return level
            
            level += 1

    def _initialize_level(self):
        """Calcule le niveau de départ de l'utilisateur sans déclencher d'événement."""
        self.current_level = self._get_level_from_points(self.total_points)
        logger.info(f"Niveau initial de l'utilisateur : {self.current_level}")

    def _check_for_level_up(self):
        """Vérifie si le total de points actuel résulte en un changement de niveau."""
        calculated_level = self._get_level_from_points(self.total_points)

        if calculated_level > self.current_level:
            logger.info(f"BRAVO ! Vous êtes passé du niveau {self.current_level} au niveau {calculated_level} !")
            self.current_level = calculated_level
            self._event_manager.publish('level_up', new_level=self.current_level)