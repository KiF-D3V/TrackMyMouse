# modules/level/xp_repository.py

import sqlite3
from utils.paths import get_db_path

class XPRepository:
    """
    Gère l'accès à la table user_progress dans la base de données.
    """
    def __init__(self):
        """Initialise la connexion à la base de données."""
        db_path = get_db_path()
        
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        """Crée la table user_progress si elle n'existe pas."""
        # La colonne unlocked_badges est prévue pour le futur.
        query = """
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY,
            total_points INTEGER NOT NULL DEFAULT 0,
            unlocked_badges TEXT
        );
        """
        with self._conn:
            self._conn.execute(query)

    def get_total_points(self) -> int:
        """Récupère le total des points de l'utilisateur."""
        # Nous nous attendons à n'avoir qu'une seule ligne pour l'utilisateur.
        query = "SELECT total_points FROM user_progress WHERE id = 1;"
        cursor = self._conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else 0

    def save_total_points(self, points: int):
        """Sauvegarde le total des points de l'utilisateur."""
        # "INSERT OR IGNORE" pour la première fois, "UPDATE" ensuite.
        # C'est une manière atomique de gérer l'insertion/mise à jour.
        query = "INSERT INTO user_progress (id, total_points) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET total_points = excluded.total_points;"
        with self._conn:
            self._conn.execute(query, (points,))

    def close(self):
        """Ferme la connexion à la base de données."""
        self._conn.close()