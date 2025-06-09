# Changelog

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

## [0.5.0] - 2025-06-09

### Added
- **Personnalisation de l'interface :** Ajout d'une section "Affichage" dans les Paramètres pour activer ou désactiver les onglets "Historique", "Records" et "Badges".
- **Nouvel onglet "Records" :** La section des records a été déplacée de l'onglet "Historique" vers son propre onglet dédié pour plus de clarté.

### Changed
- **Architecture de l'onglet Paramètres :** Refactoring complet de l'onglet en plusieurs composants indépendants pour améliorer la stabilité et la maintenabilité.
- **Architecture de l'UI principale :** `MainWindow` charge maintenant les onglets de manière dynamique en fonction des préférences de l'utilisateur.

### Fixed
- **Stabilité des Paramètres :** Correction d'une série de bugs complexes qui empêchaient la mise à jour correcte de l'interface lors du changement de langue ou d'unité.
- **Premier Lancement :** Correction d'un bug qui provoquait l'affichage en boucle de la fenêtre de premier lancement.


## [0.4.0] - 2025-06-07

### Ajouté (Added)
- Nouvelle section "Records" dans l'onglet Historique : affiche le jour de la plus grande distance et le jour de la plus grande activité.

### Modifié (Changed)
- Amélioration de l'ergonomie de l'onglet Historique : les sections sont maintenant réduites par défaut et fonctionnent en "accordéon".
- Refonte de la gestion des statistiques pour une meilleure maintenabilité.


## [0.3.0] - 2025-06-06

### Modifié (Changed)
- Amélioration majeure de la structure des dossiers du projet pour une meilleure organisation et maintenabilité.


## [0.2.0] - 2025-06-04

### Ajouté (Added)
- Nouvel onglet "Historique" avec affichage des N derniers jours de statistiques (période sélectionnable, section affichable/masquable).
- Choix de la langue de l'application dès le dialogue de premier lancement.

### Modifié (Changed)
- Précision de la date (Heure:Minute:Seconde) unifiée entre les préférences utilisateurs, et la date de lancement.
- Ajustement des largeurs de colonnes dans le tableau de l'onglet Historique.


## [0.1.0] - 2025-06-03 
Première version de développement. Cette version pose les fondations de TrackMyMouse avec les premières fonctionnalités et corrections.

### Ajouté (Added)
- Système de journalisation (logs) pour suivre le fonctionnement de l'application.
- Gestionnaire dédié pour l'icône de l'application dans la barre système.
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