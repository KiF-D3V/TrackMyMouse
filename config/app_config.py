# config/app_config.py

"""
Fichier central pour les constantes de configuration de l'application.
"""

# --- Application Core ---
APP_NAME = "TrackMyMouse"
APP_AUTHOR = "TrackMyMouse"

# --- File Names ---
DB_FILENAME = "stats.db"
PREFERENCES_FILENAME = "user_preferences.ini"

# --- Stats & Activity Tracking ---
INACTIVITY_THRESHOLD_SECONDS = 2
ACTIVITY_TRACKER_INTERVAL = 1

# --- GUI (Graphical User Interface) ---
HISTORY_DAYS_OPTIONS = [7, 14, 30]

# --- REGISTRE DES ONGLETS OPTIONNELS (ajout onglet = penser au fichier de langue)---
OPTIONAL_TABS = [
    {
        "id": "history",
        "title_key": "history_tab_title",
        "preference_key": "show_history_tab",
        "toggle_label_key": "show_history_tab_label",
        "module_path": "gui.history_tab",
        "class_name": "HistoryTab"
    },
    {
        "id": "records",
        "title_key": "records_tab_title",
        "preference_key": "show_records_tab",
        "toggle_label_key": "show_records_tab_label",
        "module_path": "gui.records_tab",
        "class_name": "RecordsTab"
    },
    {
        "id": "rainmeter",
        "title_key": "rainmeter_tab_title",
        "preference_key": "show_rainmeter_tab",
        "toggle_label_key": "show_rainmeter_tab_label",
        "module_path": "modules.rainmeter.rainmeter_tab",
        "class_name": "RainmeterTab"
    }
]
