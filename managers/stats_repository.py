# managers/stats_repository.py

import sqlite3
import logging
from typing import Optional, List, Dict, Any

from utils.paths import get_db_path

class StatsRepository:
    """
    Couche d'accès aux données (Repository) pour toutes les opérations
    liées à la base de données de statistiques (stats.db).
    Cette classe gère la connexion, le curseur, et toutes les requêtes SQL.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_path = get_db_path()
        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._connect_db()

    def _connect_db(self):
        """Établit la connexion à la base de données et crée les tables si elles n'existent pas."""
        self.logger.info(f"Repository : Connexion à la base de données : {self.db_path}")
        try:
            # La création du dossier est gérée par get_db_path()
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._cursor = self._conn.cursor()
            self._create_tables()
            self.logger.info("Repository : Connexion à la BDD établie et tables vérifiées.")
        except (sqlite3.Error, OSError) as e:
            self.logger.critical(f"Repository : Erreur critique lors de la connexion à la BDD '{self.db_path}': {e}", exc_info=True)
            raise

    def _create_tables(self):
        """Crée les tables 'daily_stats' et 'app_settings' si elles n'existent pas."""
        if not self._cursor:
            self.logger.error("Repository : Impossible de créer les tables, curseur non disponible.")
            return
        self.logger.debug("Repository : Vérification/création des tables.")
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
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        if self._conn:
            self._conn.commit()

    def get_daily_stats(self, date_iso: str) -> Optional[Dict[str, Any]]:
        """Récupère les statistiques pour une date spécifique."""
        if not self._cursor: return None
        self.logger.debug(f"Repository : Récupération des stats pour la date : {date_iso}")
        self._cursor.execute("SELECT * FROM daily_stats WHERE date = ?", (date_iso,))
        row = self._cursor.fetchone()
        return dict(row) if row else None

    def create_daily_stats_entry(self, date_iso: str):
        """Crée une nouvelle entrée pour un jour donné dans la table daily_stats."""
        if not self._cursor or not self._conn: return
        self.logger.info(f"Repository : Création d'une nouvelle entrée pour la date : {date_iso}")
        self._cursor.execute("INSERT INTO daily_stats (date) VALUES (?)", (date_iso,))
        self._conn.commit()

    def update_daily_stats(self, stats_dict: Dict[str, Any]):
        """Met à jour une entrée de statistiques journalières."""
        if not self._cursor or not self._conn: return
        self.logger.debug(f"Repository : Mise à jour des stats pour la date : {stats_dict.get('date')}")
        self._cursor.execute('''
            UPDATE daily_stats
            SET distance_pixels = ?, left_clicks = ?, right_clicks = ?, middle_clicks = ?,
                active_time_seconds = ?, inactive_time_seconds = ?
            WHERE date = ?
        ''', (
            stats_dict.get('distance_pixels', 0.0),
            stats_dict.get('left_clicks', 0),
            stats_dict.get('right_clicks', 0),
            stats_dict.get('middle_clicks', 0),
            stats_dict.get('active_time_seconds', 0),
            stats_dict.get('inactive_time_seconds', 0),
            stats_dict.get('date')
        ))
        # Le commit est souvent géré par une méthode save() plus globale

    def get_app_setting(self, key: str) -> Optional[str]:
        """Récupère une valeur depuis la table app_settings."""
        if not self._cursor: return None
        self._cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = self._cursor.fetchone()
        return row['value'] if row else None

    def set_app_setting(self, key: str, value: str):
        """Définit une valeur dans la table app_settings."""
        if not self._cursor or not self._conn: return
        self.logger.info(f"Repository : Définition du paramètre '{key}' à '{value}'.")
        self._cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value))
        self._conn.commit()
    
    def get_global_stats(self) -> Optional[Dict[str, Any]]:
        """Calcule et retourne les statistiques agrégées."""
        if not self._cursor: return None
        self.logger.debug("Repository : Calcul des statistiques globales.")
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
        return dict(row) if row else None

    def get_last_n_days_stats(self, num_days: int) -> List[Dict[str, Any]]:
        """Récupère les statistiques des N derniers jours."""
        if not self._cursor or num_days <= 0: return []
        self.logger.debug(f"Repository : Récupération des {num_days} derniers jours.")
        query = "SELECT * FROM daily_stats ORDER BY date DESC LIMIT ?"
        self._cursor.execute(query, (num_days,))
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]

    def save_changes(self):
        """Valide (commit) les transactions en attente sur la base de données."""
        if self._conn:
            self.logger.debug("Repository : Sauvegarde des changements (commit).")
            self._conn.commit()

    def close(self):
        """Ferme la connexion à la base de données."""
        if self._conn:
            self.logger.info("Repository : Fermeture de la connexion à la BDD.")
            self.save_changes() # Sauvegarde une dernière fois avant de fermer
            self._conn.close()
            self._conn = None