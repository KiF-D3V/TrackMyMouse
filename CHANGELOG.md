# Changelog

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

## [0.8.0] - 2025-06-20

### ♻️ Changed
- **Fiabilité et Stabilité Accrues :** L'architecture interne de l'application a été entièrement réorganisée. Ce grand refactoring rend l'application plus robuste, plus rapide au démarrage et prépare le terrain pour les futures évolutions de manière plus saine.

### 🐛 Fixed
- **Correction de Bugs :** Plusieurs erreurs potentielles qui pouvaient survenir lors de l'initialisation des différents modules ont été résolues grâce à cette nouvelle architecture.

---

## [0.7.0] - 2025-06-19

### ✨ Added
- **Nouveau look pour l'onglet "Niveau" !** Pour mieux suivre votre progression, votre niveau est maintenant affiché en plus gros et en couleur. La barre de progression a également été redessinée pour être plus visible.

### ♻️ Changed
- **Amélioration des performances et de la stabilité.** Une large partie du code interne a été réécrite pour rendre l'application plus robuste et plus facile à mettre à jour à l'avenir.
- **Meilleur suivi des erreurs.** Le système de journalisation a été amélioré pour nous permettre de diagnostiquer et corriger les bugs plus efficacement.

### 🐛 Fixed
- Correction d'un bug majeur qui pouvait arrêter le suivi de la souris après un clic droit ou après avoir restauré l'application depuis la barre des tâches.
- Correction d'un problème où l'icône dans la barre des tâches (systray) pouvait ne pas s'afficher correctement au démarrage.
- Correction d'un bug qui empêchait la fenêtre de bienvenue et de configuration de s'afficher pour les nouveaux utilisateurs.
- Résolution de plusieurs erreurs qui pouvaient survenir au démarrage de l'application suite aux récentes modifications.

---

## [0.6.1] - 2025-06-16

### 🐛 Fixed
- **Démarrage :** Correction d'un problème qui pouvait empêcher l'application de démarrer correctement après son installation.
- **Onglets :** Correction des onglets qui ne s'affichaient pas au démarrage. L'affichage des onglets est maintenant plus fluide et plus fiable.

---

## [0.6.0] - 2025-06-15

### ✨ Added
- **Module gamification Niveau/XP :** Ajout d'un onglet "Niveau" pour consulter le nombre d'XP ainsi que le Niveau actuel.
- **Onglet Niveau optionnel :** Intégration de l'onglet comme un onglet optionnel "data-driven" via le registre OPTIONAL_TABS
- **Utilitaires :** Création d'un nouveau fichier avec une fonction calculate_distance pour centraliser le calcul de distance (principe DRY).
- **Evénements :** Le XPManager publie maintenant un nouvel événement level_up lors d'un passage de niveau.

### ♻️ Changed
- **Architecture UI :** La boucle de rafraîchissement des onglets actifs plus fluide et satble.
- **Harmonisation :** La méthode de mise à jour de TodayTab a été renommée update_display pour plus de cohérence.
- **Refactorisation :** Le StatsManager utilise maintenant la fonction utilitaire partagée calculate_distance.

### 🐛 Fixed
- **Correction d'erreurs :** Correction de nombreuses erreurs de démarrage. Découvertes et résolues pendant le processus de développement du module et onglet "Niveau".

---

## [0.5.0] - 2025-06-09

### ✨ Added
- **Personnalisation de l'interface :** Ajout d'une section "Affichage" dans les Paramètres pour activer ou désactiver les différents onglets.
- **Nouvel onglet "Records" :** La section des records a été déplacée de l'onglet "Historique" vers son propre onglet dédié pour plus de clarté.

### ♻️ Changed
- **Architecture de l'onglet Paramètres :** Refactoring complet de l'onglet en plusieurs composants indépendants pour améliorer la stabilité et la maintenabilité.
- **Architecture de l'UI principale :** Les onglets se chargent de manière dynamique en fonction des préférences de l'utilisateur.

### 🐛 Fixed
- **Stabilité des Paramètres :** Correction d'une série de bugs complexes qui empêchaient la mise à jour correcte de l'interface lors du changement de langue ou d'unité.
- **Premier Lancement :** Correction d'un bug qui provoquait l'affichage en boucle de la fenêtre de premier lancement.

---

## [0.4.0] - 2025-06-07

### ✨ Added
- Nouvel onglet "Records" : affiche le jour de la plus grande distance et le jour de la plus grande activité.

### ♻️ Changed
- Amélioration de l'ergonomie de l'onglet Historique.
- Refonte de la gestion des statistiques pour une meilleure maintenabilité.

---

## [0.3.0] - 2025-06-06

### ♻️ Changed
- Amélioration majeure de la structure des dossiers du projet pour une meilleure organisation et maintenabilité.

---

## [0.2.0] - 2025-06-04

### ✨ Added
- Nouvel onglet "Historique" avec affichage des N derniers jours de statistiques (période sélectionnable, section affichable/masquable).
- Choix de la langue de l'application dès le dialogue de premier lancement.

### ♻️ Changed
- Précision de la date (Heure:Minute:Seconde) unifiée entre les préférences utilisateurs, et la date de lancement.
- Ajustement des largeurs de colonnes dans le tableau de l'onglet Historique.

---

## [0.1.0] - 2025-06-03 
Première version de développement. Cette version pose les fondations de TrackMyMouse avec les premières fonctionnalités et corrections.

### ✨ Added
- Système de journalisation (logs) pour suivre le fonctionnement de l'application.
- Gestionnaire dédié pour l'icône de l'application dans la barre système.
- Logger intégré pour un meilleur suivi des opérations de données.

### ♻️ Changed
- Amélioration de la structure du code principal pour plus de clarté.
- Optimisation de la fermeture de l'application depuis l'icône de la barre système pour une meilleure stabilité.
- Précision de la date de 1er lancement stockée (Heure:Minute:Seconde) et correction de son initialisation dans la base de données.
- Ordre d'affichage des clics souris modifié (Gauche | Milieu | Droite) dans l'interface.
- Refactoring de la méthode d'affichage des statistiques pour une meilleure séparation des préoccupations.

### 🐛 Fixed
- Problème technique qui pouvait survenir lors de la fermeture via l'icône de la barre système.
- Assure que le dialogue de configuration au premier lancement s'affiche correctement.
- Correction d'une erreur qui empêchait l'affichage des statistiques.
- Formatage correct de la date de premier lancement en français (`JJ/MM/AAAA HH:MM:SS`).