# Changelog

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

## [0.1.0] - 2025-06-02

Première version de développement. Cette version pose les fondations de TrackMyMouse avec les premières fonctionnalités et corrections.

### Ajouté (Added)
- Intégration d'un système de journalisation (logs) pour mieux suivre l'activité de l'application.
- Mise en place d'un module distinct pour gérer l'icône de l'application dans la barre système (`SystrayManager`).

### Modifié (Changed)
- Amélioration de la structure du code principal (`main.py`) pour plus de clarté.
- Optimisation de la fermeture de l'application depuis l'icône de la barre système pour une meilleure stabilité.

### Corrigé (Fixed)
- Correction d'un problème technique qui pouvait survenir lors de la fermeture via l'icône de la barre système.
- Assure que le dialogue de configuration au premier lancement s'affiche correctement.