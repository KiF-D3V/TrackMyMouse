# main.py

import tkinter as tk
import logging

from utils.logging_setup import setup_logging
from core.application import MouseTrackerApp

if __name__ == "__main__":
    setup_logging()
    main_logger = logging.getLogger(__name__)
    
    try:
        main_logger.info("Démarrage de l'application TrackMyMouse...")
        root = tk.Tk()
        app = MouseTrackerApp(root)
        root.mainloop()
        main_logger.info("Application terminée proprement.")
    except Exception as e:
        main_logger.critical(f"Erreur fatale non gérée au niveau racine : {e}", exc_info=True)