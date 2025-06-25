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
INACTIVITY_THRESHOLD_SECONDS = 5
ACTIVITY_TRACKER_INTERVAL = 1

# --- XP/Level System ---
XP_SAVE_INTERVAL_SECONDS = 3600 # 1 heure

# --- GUI (Graphical User Interface) ---
HISTORY_DAYS_OPTIONS = [7, 14, 30]

# --- REGISTRE DES ONGLETS STATIQUES ET OPTIONNELS---
# Onglets statiques du début
STATIC_TABS_START = [
    {"id": "today", "title_key": "today_tab_title", "icon_filename": "today_tab_icon.png", "module_path": "gui.today_tab", "class_name": "TodayTab"},
]

# Onglets optionnels
OPTIONAL_TABS = [
    {
        "id": "history",
        "title_key": "history_tab_title",
        "icon_filename": "history_tab_icon.png",
        "preference_key": "show_history_tab",
        "toggle_label_key": "show_history_tab_label",
        "module_path": "gui.history_tab",
        "class_name": "HistoryTab"
    },
    {
        "id": "records",
        "title_key": "records_tab_title",
        "icon_filename": "records_tab_icon.png",
        "preference_key": "show_records_tab",
        "toggle_label_key": "show_records_tab_label",
        "module_path": "gui.records_tab",
        "class_name": "RecordsTab"
    },
    {
        "id": "level",
        "title_key": "level_tab_title",
        "icon_filename": "level_tab_icon.png",
        "preference_key": "show_level_tab",
        "toggle_label_key": "show_level_tab_label",
        "module_path": "modules.level.level_tab",
        "class_name": "LevelTab"
    },
    {
        "id": "rainmeter",
        "title_key": "rainmeter_tab_title",
        "icon_filename": "rainmeter_tab_icon.png",
        "preference_key": "show_rainmeter_tab",
        "toggle_label_key": "show_rainmeter_tab_label",
        "module_path": "modules.rainmeter.rainmeter_tab",
        "class_name": "RainmeterTab"
    }
]

# Onglets statiques de fin
STATIC_TABS_END = [
    {"id": "settings", "title_key": "settings_tab_title", "icon_filename": "settings_tab_icon.png", "module_path": "gui.settings_tab", "class_name": "SettingsTab"},
    {"id": "about", "title_key": "about_tab_title", "icon_filename": "about_tab_icon.png", "module_path": "gui.about_tab", "class_name": "AboutTab"},
]
