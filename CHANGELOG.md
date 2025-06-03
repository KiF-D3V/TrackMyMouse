# Changelog

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

## [0.1.0] - 2025-06-03 Première version de développement. Cette version pose les fondations de TrackMyMouse avec les premières fonctionnalités et corrections.

### Ajouté (Added)
- Système de journalisation (logs) pour suivre le fonctionnement de l'application.
- Gestionnaire dédié pour l'icône de l'application dans la barre système (`SystrayManager`).
- Logger intégré dans `StatsManager` pour un meilleur suivi des opérations de données.

### Modifié (Changed)
- Amélioration de la structure du code principal (`main.py`) pour plus de clarté.
- Optimisation de la fermeture de l'application depuis l'icône de la barre système pour une meilleure stabilité.
- Précision de la `first_launch_date` stockée (Heure:Minute:Seconde) et correction de son initialisation dans la base de données.
- Ordre d'affichage des clics souris modifié (Gauche | Milieu | Droite) dans l'interface.
- Refactoring de la méthode d'affichage des statistiques dans `MainWindow` pour une meilleure séparation des préoccupations.

### Corrigé (Fixed)
- Problème technique qui pouvait survenir lors de la fermeture via l'icône de la barre système.
- Assure que le dialogue de configuration au premier lancement s'affiche correctement.
- Correction d'une `AttributeError` dans `StatsManager` qui empêchait l'affichage des statistiques.
- Formatage correct de la date de premier lancement en français (`JJ/MM/AAAA HH:MM:SS`).