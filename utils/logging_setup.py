# utils/logging_setup.py

import os
import json
import logging
import logging.config
from utils.paths import resource_path

def setup_logging(default_path='config/logging_config.json', default_level=logging.INFO):
    """
    Configure le logging en utilisant un fichier de configuration JSON.

    Si le fichier de configuration n'est pas trouvé ou est invalide,
    une configuration de base est mise en place pour que l'application
    puisse quand même fonctionner avec des logs.
    """
    config_path = resource_path(default_path)
    if os.path.exists(config_path):
        try:
            with open(config_path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
            logging.info("Configuration du logging chargée avec succès depuis le fichier JSON.")
        except Exception as e:
            logging.basicConfig(level=default_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logging.warning(f"Erreur lors du chargement de la config de logging depuis {config_path}. Utilisation de la config de base. Erreur: {e}")
    else:
        logging.basicConfig(level=default_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.info(f"Fichier de config de logging non trouvé. Utilisation de la config de base.")