# managers/stats_manager.py

import sqlite3
import datetime
import os
import time
import threading 
import logging 
from pynput import mouse # type: ignore
from typing import Optional, List, Dict, Any 

# --- MODIFIÉ : Remplacement des imports liés au chemin ---
# L'import d'appdirs n'est plus nécessaire ici.
from managers.preference_manager import PreferenceManager
from utils.service_locator import service_locator
# AJOUT : Import de la nouvelle fonction de gestion de chemin
from utils.paths import get_db_path

# --- Constants ---
# La logique pour DB_FILENAME et APP_NAME_FOR_DIRS est maintenant dans utils/paths.py
# On conserve uniquement les constantes propres à ce manager.
INACTIVITY_THRESHOLD_SECONDS = 2 

class StatsManager:
    """
    Gère toutes les statistiques liées à la souris et à l'application, 
    en utilisant SQLite pour la persistance des données.
    Cette classe encapsule toute la logique de la base de données et est conçue pour être thread-safe.
    Elle suit la distance de la souris, les clics et le temps d'activité de l'utilisateur.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__) 
        self.logger.info("Initialisation de StatsManager...")

        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._db_lock = threading.Lock() 
        
        # --- MODIFIÉ : Utilisation de la fonction centralisée pour obtenir le chemin de la BDD ---
        self.db_full_path = get_db_path()
        # --- FIN DE LA MODIFICATION ---
        
        self.today = datetime.date.today().isoformat()
        self.last_mouse_position: Optional[tuple[int, int]] = None
        self.last_activity_time: float = time.time()
        self.is_active: bool = True 
        self._stop_tracker: bool = False

        self._connect_db() 
        
        self._current_day_stats_in_memory: dict = self._get_or_create_todays_entry()
        self._initialize_app_settings() 

        self._activity_tracker_thread = threading.Thread(target=self._run_activity_tracker, daemon=True)
        self._activity_tracker_thread.start()
        self.logger.info("StatsManager initialisé et tracker d'activité démarré.")

    def _connect_db(self):
        """Établit la connexion à la base de données SQLite et crée les tables si elles n'existent pas."""
        self.logger.info(f"Tentative de connexion à la base de données : {self.db_full_path}")
        try:
            # La création du dossier est gérée par get_db_path() dans utils/paths.py,
            # donc plus besoin de os.makedirs ici.
            self._conn = sqlite3.connect(self.db_full_path, check_same_thread=False) 
            if self._conn: 
                self._conn.row_factory = sqlite3.Row 
                self._cursor = self._conn.cursor()
                with self._db_lock: 
                    self._create_tables()
                self.logger.info(f"Connexion à la base de données établie ({self.db_full_path}) et tables vérifiées/créées.")
            else:
                self.logger.critical("Échec de l'établissement de la connexion à la base de données, _conn est None.")
        except sqlite3.Error as e:
            self.logger.critical(f"Erreur SQLite lors de la connexion ou de la création des tables pour '{self.db_full_path}': {e}", exc_info=True)
            raise 
        except OSError as e: 
            self.logger.critical(f"Erreur OS lors de la tentative de connexion à '{self.db_full_path}': {e}", exc_info=True)
            raise

    # ... [ TOUT LE RESTE DU FICHIER RESTE INCHANGÉ ] ...
    # Collez ici la suite de votre fichier, à partir de la méthode _create_tables()
    # jusqu'à la fin.

    # Le reste du fichier (méthodes _create_tables, _initialize_app_settings, etc.)
    # reste identique à la version que vous m'avez fournie (celle du Tour 36),
    # car ces méthodes utilisent self._conn et self._cursor qui sont maintenant initialisés
    # avec la base de données au nouvel emplacement.
    # J'inclus tout le reste pour que vous ayez le fichier complet.

    def _create_tables(self):
        """Crée les tables nécessaires (daily_stats et app_settings) si elles n'existent pas."""
        if not self._cursor or not self._conn:
            self.logger.error("Impossible de créer les tables: curseur ou connexion non initialisé.")
            return
        try:
            self.logger.debug("Création/vérification de la table 'daily_stats'.")
            self._cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    distance_pixels REAL DEFAULT 0.0,
                    left_clicks INTEGER DEFAULT 0,
                    right_clicks INTEGER DEFAULT 0,
                    middle_clicks INTEGER DEFAULT 0,
                    active_time_seconds INTEGER DEFAULT 0,
                    inactive_time_seconds INTEGER DEFAULT 0
                )
            ''')
            self.logger.debug("Création/vérification de la table 'app_settings'.")
            self._cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            self._conn.commit()
            self.logger.info("Tables 'daily_stats' et 'app_settings' assurées d'exister.")
        except sqlite3.Error as e:
            self.logger.error(f"Erreur SQLite lors de la création des tables: {e}", exc_info=True)


    def _initialize_app_settings(self):
        """
        S'assure que les paramètres essentiels de l'application (comme la date de premier lancement) 
        sont présents dans la base de données.
        La date de premier lancement est lue depuis PreferenceManager.
        """
        if not self._cursor or not self._conn:
            self.logger.error("Impossible d'initialiser app_settings: curseur ou connexion non initialisé.")
            return

        with self._db_lock: 
            try:
                self.logger.debug("Vérification de 'first_launch_date' dans app_settings.")
                self._cursor.execute("SELECT value FROM app_settings WHERE key = 'first_launch_date'")
                if self._cursor.fetchone() is None:
                    self.logger.info("'first_launch_date' non trouvée dans la BDD. Tentative de lecture depuis PreferenceManager.")
                    try:
                        preference_manager: PreferenceManager = service_locator.get_service("preference_manager")
                        first_launch_date_str = preference_manager.get_first_launch_date()
                        self.logger.info(f"Insertion de 'first_launch_date' ({first_launch_date_str}) dans la BDD.")
                        self._cursor.execute(
                            "INSERT INTO app_settings (key, value) VALUES (?, ?)", 
                            ('first_launch_date', first_launch_date_str)
                        )
                        self._conn.commit()
                        self.logger.info("'first_launch_date' initialisée dans la BDD avec succès.")
                    except Exception as e: 
                        self.logger.error(f"Erreur lors de la récupération ou de l'insertion de 'first_launch_date' depuis PreferenceManager: {e}", exc_info=True)
                else:
                    self.logger.debug("'first_launch_date' déjà présente dans la BDD.")
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite lors de l'initialisation de app_settings: {e}", exc_info=True)


    def _get_or_create_todays_entry(self) -> dict:
        """
        Récupère les statistiques du jour depuis la base de données ou crée une nouvelle entrée si aucune n'existe.
        Retourne les statistiques du jour courant sous forme de dictionnaire.
        """
        if not self._cursor or not self._conn:
            self.logger.error("Impossible d'obtenir l'entrée du jour: curseur ou connexion non initialisé.")
            return self._get_initial_daily_stats_structure()

        with self._db_lock:
            try:
                self.logger.debug(f"Recherche des stats pour la date: {self.today}")
                self._cursor.execute(
                    "SELECT * FROM daily_stats WHERE date = ?", 
                    (self.today,)
                )
                row = self._cursor.fetchone()

                if row is None:
                    self.logger.info(f"Aucune entrée pour {self.today}, création d'une nouvelle entrée.")
                    self._cursor.execute(
                        "INSERT INTO daily_stats (date) VALUES (?)", 
                        (self.today,)
                    )
                    self._conn.commit() 
                    self._cursor.execute(
                        "SELECT * FROM daily_stats WHERE date = ?", 
                        (self.today,)
                    )
                    row = self._cursor.fetchone()
                    self.logger.info(f"Nouvelle entrée créée pour {self.today}.")
                else:
                    self.logger.debug(f"Entrée trouvée pour {self.today}.")
                
                return dict(row) if row else self._get_initial_daily_stats_structure()
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite dans _get_or_create_todays_entry: {e}", exc_info=True)
                return self._get_initial_daily_stats_structure()


    def _update_todays_entry_in_db(self):
        """Met à jour les statistiques du jour courant dans la base de données avec les valeurs en mémoire."""
        if not self._cursor or not self._conn:
            self.logger.error("Impossible de mettre à jour l'entrée du jour en BDD: curseur ou connexion non initialisé.")
            return
            
        self.logger.debug(f"Mise à jour de l'entrée du jour ({self.today}) dans la BDD.")
        with self._db_lock: 
            try:
                self._cursor.execute('''
                    UPDATE daily_stats
                    SET distance_pixels = ?, left_clicks = ?, right_clicks = ?, middle_clicks = ?,
                        active_time_seconds = ?, inactive_time_seconds = ?
                    WHERE date = ?
                ''', (
                    self._current_day_stats_in_memory['distance_pixels'],
                    self._current_day_stats_in_memory['left_clicks'],
                    self._current_day_stats_in_memory['right_clicks'],
                    self._current_day_stats_in_memory['middle_clicks'],
                    self._current_day_stats_in_memory['active_time_seconds'],
                    self._current_day_stats_in_memory['inactive_time_seconds'],
                    self.today
                ))
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite dans _update_todays_entry_in_db: {e}", exc_info=True)


    def _run_activity_tracker(self):
        """
        Thread qui vérifie périodiquement l'activité de la souris pour mettre à jour le temps actif/inactif.
        Gère également le basculement quotidien des statistiques.
        """
        self.logger.info("Thread de suivi d'activité démarré.")
        while not self._stop_tracker:
            time.sleep(1) 
            if self._stop_tracker:
                self.logger.debug("Signal d'arrêt reçu par le tracker d'activité (après sleep).")
                break

            current_time = time.time()
            time_since_last_activity = current_time - self.last_activity_time

            current_date = datetime.date.today().isoformat()
            if self.today != current_date:
                self.logger.info(f"Nouveau jour détecté: {current_date}. Ancien jour: {self.today}.")
                self.save_changes() 
                self.today = current_date
                self._current_day_stats_in_memory = self._get_or_create_todays_entry()
                self.last_activity_time = current_time 
                self.is_active = True 
                self.logger.info(f"Statistiques réinitialisées pour le nouveau jour: {self.today}.")

            if time_since_last_activity <= INACTIVITY_THRESHOLD_SECONDS:
                if not self.is_active:
                    self.logger.debug("Transition: Inactif -> Actif")
                    self.is_active = True
                self._current_day_stats_in_memory['active_time_seconds'] += 1
            else:
                if self.is_active:
                    self.logger.debug("Transition: Actif -> Inactif")
                    self.is_active = False
                self._current_day_stats_in_memory['inactive_time_seconds'] += 1
        self.logger.info("Thread de suivi d'activité terminé.")


    def increment_click(self, button: mouse.Button):
        """
        Incrémente le compteur de clics pour le bouton de souris spécifié.
        """
        current_date = datetime.date.today().isoformat()
        if self.today != current_date: 
            self.logger.info(f"Changement de jour détecté dans increment_click (de {self.today} à {current_date}).")
            self.save_changes() 
            self.today = current_date
            self._current_day_stats_in_memory = self._get_or_create_todays_entry() 

        if button == mouse.Button.left:
            self._current_day_stats_in_memory['left_clicks'] += 1
        elif button == mouse.Button.right:
            self._current_day_stats_in_memory['right_clicks'] += 1
        elif button == mouse.Button.middle:
            self._current_day_stats_in_memory['middle_clicks'] += 1
        
        self.logger.debug(f"Clic {button} incrémenté. Stats du jour: L={self._current_day_stats_in_memory['left_clicks']}, M={self._current_day_stats_in_memory['middle_clicks']}, R={self._current_day_stats_in_memory['right_clicks']}")
        
        self.last_activity_time = time.time()
        if not self.is_active: 
            self.logger.debug("Clic détecté pendant inactivité, passage à actif.")
            self.is_active = True


    def update_mouse_position(self, x: int, y: int):
        """
        Met à jour la distance totale de la souris en fonction de la nouvelle position.
        """
        current_time = time.time()
        
        current_date = datetime.date.today().isoformat()
        if self.today != current_date: 
            self.logger.info(f"Changement de jour détecté dans update_mouse_position (de {self.today} à {current_date}).")
            self.save_changes() 
            self.today = current_date
            self._current_day_stats_in_memory = self._get_or_create_todays_entry() 

        if self.last_mouse_position:
            last_x, last_y = self.last_mouse_position
            distance = ((x - last_x)**2 + (y - last_y)**2)**0.5
            self._current_day_stats_in_memory['distance_pixels'] += distance

        self.last_mouse_position = (x, y)
        self.last_activity_time = current_time 
        if not self.is_active: 
            self.logger.debug("Mouvement détecté pendant inactivité, passage à actif.")
            self.is_active = True 
        

    def get_todays_stats(self) -> dict:
        """Retourne les statistiques du jour courant depuis la mémoire."""
        return self._current_day_stats_in_memory


    def get_global_stats(self) -> dict:
        """
        Calcule et retourne les statistiques agrégées de tous les jours enregistrés dans la base de données.
        S'assure que les changements du jour courant sont sauvegardés avant la requête.
        """
        self.logger.debug("Demande de récupération des statistiques globales.")
        self.save_changes()

        with self._db_lock: 
            if not self._cursor:
                self.logger.error("Impossible de récupérer les stats globales: curseur non initialisé.")
                return self._get_empty_global_stats_structure()
            try:
                self._cursor.execute('''
                    SELECT
                        SUM(distance_pixels) AS total_distance_pixels,
                        SUM(left_clicks) AS total_left_clicks,
                        SUM(right_clicks) AS total_right_clicks,
                        SUM(middle_clicks) AS total_middle_clicks,
                        SUM(active_time_seconds) AS total_active_time_seconds,
                        SUM(inactive_time_seconds) AS total_inactive_time_seconds
                    FROM daily_stats
                ''')
                row = self._cursor.fetchone()
                log_row_data = dict(row) if row and all(k in row.keys() for k in row.keys()) else 'None ou données partielles'
                self.logger.debug(f"Stats globales brutes récupérées de la BDD: {log_row_data}")
                
                return {
                    'total_distance_pixels': row['total_distance_pixels'] if row and row['total_distance_pixels'] is not None else 0.0,
                    'left_clicks': row['total_left_clicks'] if row and row['total_left_clicks'] is not None else 0,
                    'right_clicks': row['total_right_clicks'] if row and row['total_right_clicks'] is not None else 0,
                    'middle_clicks': row['total_middle_clicks'] if row and row['total_middle_clicks'] is not None else 0,
                    'total_active_time_seconds': row['total_active_time_seconds'] if row and row['total_active_time_seconds'] is not None else 0,
                    'total_inactive_time_seconds': row['total_inactive_time_seconds'] if row and row['total_inactive_time_seconds'] is not None else 0,
                }
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite dans get_global_stats: {e}", exc_info=True)
                return self._get_empty_global_stats_structure()


    def get_first_launch_date(self) -> Optional[str]:
        """Récupère la date de premier lancement enregistrée de l'application."""
        with self._db_lock: 
            if not self._cursor:
                self.logger.error("Impossible de récupérer la date de premier lancement: curseur non initialisé.")
                return None
            try:
                self._cursor.execute("SELECT value FROM app_settings WHERE key = 'first_launch_date'")
                row = self._cursor.fetchone()
                date_val = row['value'] if row else None
                return date_val
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite dans get_first_launch_date: {e}", exc_info=True)
                return None

    def get_last_n_days_stats(self, num_days: int) -> List[Dict[str, Any]]:
        """
        Récupère les statistiques complètes pour les `num_days` jours les plus récents
        ayant des entrées dans la table `daily_stats`.

        Args:
            num_days: Le nombre de jours d'historique à récupérer.

        Returns:
            Une liste de dictionnaires, chaque dictionnaire représentant les statistiques d'un jour.
            La liste est triée de la date la plus récente à la plus ancienne.
            Retourne une liste vide en cas d'erreur ou si aucune donnée n'est trouvée.
        """
        self.logger.info(f"Demande de récupération des statistiques des {num_days} derniers jours.")
        if not self._cursor:
            self.logger.error("Impossible de récupérer l'historique: curseur non initialisé.")
            return []
        if num_days <= 0:
            self.logger.warning("num_days doit être positif pour get_last_n_days_stats.")
            return []

        self.save_changes()

        query = """
            SELECT date, distance_pixels, left_clicks, right_clicks, middle_clicks, 
                   active_time_seconds, inactive_time_seconds
            FROM daily_stats
            ORDER BY date DESC
            LIMIT ?
        """
        with self._db_lock:
            try:
                self._cursor.execute(query, (num_days,))
                rows = self._cursor.fetchall()
                self.logger.debug(f"{len(rows)} lignes récupérées pour les {num_days} derniers jours.")
                return [dict(row_item) for row_item in rows] 
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite dans get_last_n_days_stats: {e}", exc_info=True)
                return []

    def reset_todays_stats(self):
        """Réinitialise toutes les statistiques du jour courant à zéro."""
        self.logger.info(f"Demande de réinitialisation des statistiques pour aujourd'hui ({self.today}).")
        with self._db_lock: 
            if not self._cursor or not self._conn:
                self.logger.error("Impossible de réinitialiser les stats du jour: curseur ou connexion non initialisé.")
                return
            try:
                self._cursor.execute('''
                    UPDATE daily_stats
                    SET distance_pixels = 0.0, left_clicks = 0, right_clicks = 0, middle_clicks = 0,
                        active_time_seconds = 0, inactive_time_seconds = 0
                    WHERE date = ?
                ''', (self.today,))
                self._conn.commit()
                self._current_day_stats_in_memory = self._get_initial_daily_stats_structure()
                self.logger.info(f"Statistiques pour {self.today} réinitialisées avec succès.")
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite lors de la réinitialisation des stats du jour: {e}", exc_info=True)


    def reset_global_stats(self):
        """Réinitialise toutes les statistiques historiques dans la base de données et réinitialise les paramètres de l'application."""
        self.logger.warning("Demande de réinitialisation GLOBALE de toutes les statistiques et paramètres.")
        with self._db_lock: 
            if not self._cursor or not self._conn:
                self.logger.error("Impossible de réinitialiser les stats globales: curseur ou connexion non initialisé.")
                return
            try:
                self.logger.debug("Suppression des données de 'daily_stats'.")
                self._cursor.execute("DELETE FROM daily_stats")
                self.logger.debug("Suppression de 'first_launch_date' de 'app_settings'.")
                self._cursor.execute("DELETE FROM app_settings WHERE key = 'first_launch_date'")
                
                self._conn.commit() 
                
                self.logger.info("Réinitialisation des paramètres de l'application (first_launch_date).")
                self._initialize_app_settings() 

                self._current_day_stats_in_memory = self._get_initial_daily_stats_structure()
                self.logger.warning("Toutes les statistiques historiques ont été réinitialisées.")
            except sqlite3.Error as e:
                self.logger.error(f"Erreur SQLite lors de la réinitialisation des stats globales: {e}", exc_info=True)


    def save_changes(self):
        """Sauvegarde les statistiques en mémoire du jour courant dans la base de données."""
        self._update_todays_entry_in_db() 
        with self._db_lock: 
            if self._conn:
                try:
                    self._conn.commit()
                except sqlite3.Error as e:
                    self.logger.error(f"Erreur SQLite lors du commit dans save_changes: {e}", exc_info=True)
            else:
                self.logger.warning("Impossible de sauvegarder les changements: connexion à la BDD non active.")


    def close(self):
        """
        Signale l'arrêt du thread de suivi d'activité, attend sa terminaison,
        sauvegarde les changements en attente et ferme la connexion à la base de données.
        """
        self.logger.info("Demande de fermeture de StatsManager.")
        self._stop_tracker = True 
        if self._activity_tracker_thread and self._activity_tracker_thread.is_alive():
            self.logger.info("Attente de la terminaison du thread de suivi d'activité...") 
            self._activity_tracker_thread.join(timeout=2.0) 
            if self._activity_tracker_thread.is_alive():
                self.logger.warning("Le thread de suivi d'activité n'a pas terminé dans le délai imparti.")
            else:
                self.logger.info("Thread de suivi d'activité terminé.")
        
        self.logger.info("Sauvegarde finale des changements avant fermeture.")
        self.save_changes() 
        with self._db_lock: 
            if self._conn:
                self.logger.info("Fermeture de la connexion à la base de données.")
                try:
                    self._conn.close()
                    self.logger.info("Connexion à la base de données fermée.")
                except sqlite3.Error as e:
                    self.logger.error(f"Erreur SQLite lors de la fermeture de la connexion: {e}", exc_info=True)
                finally: 
                    self._conn = None
                    self._cursor = None
        self.logger.info("StatsManager fermé.")


    def _get_initial_daily_stats_structure(self) -> dict:
        """Retourne un dictionnaire représentant l'état initial des statistiques journalières."""
        return {
            'date': self.today, 
            'distance_pixels': 0.0,
            'left_clicks': 0,
            'right_clicks': 0,
            'middle_clicks': 0,
            'active_time_seconds': 0,
            'inactive_time_seconds': 0
        }

    def _get_empty_global_stats_structure(self) -> dict:
        """Retourne une structure vide pour les statistiques globales en cas d'erreur."""
        return {
            'total_distance_pixels': 0.0, 'left_clicks': 0, 'right_clicks': 0, 
            'middle_clicks': 0, 'total_active_time_seconds': 0, 'total_inactive_time_seconds': 0
        }