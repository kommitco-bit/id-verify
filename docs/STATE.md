# PROJECT_STATE
Dernière mise à jour : 2026-10-16 — Jour 1 / 15

## Fait (5 lignes max)
- Arborescence id-verif/ en cours de création.
- docs/PROJECT_BRIEF.md rédigé (stack, arborescence, contrat, vocabulaire figés).
- docs/STATE.md créé (ce fichier).
- Aucun code Python encore écrit.
- Aucune dépendance installée (pas de venv, pas d'OpenCV, pas de Tesseract).

## Fichiers clés existants (chemin — rôle)
- docs/PROJECT_BRIEF.md — brief maître condensé, référence du projet.
- docs/STATE.md — ce fichier, état courant entre sessions.

## Schéma de base actuel (tables + colonnes clés)
Aucune base créée. Prévu :
- persons(id, nom, postnom, prenom, date_naissance, numero, embedding BLOB)
- verifications(id, person_id, timestamp, status, scores_json)

## Endpoints existants (méthode chemin — rôle)
Aucun. Prévu côté ESP32-CAM : GET /capture — renvoie une image JPEG.

## Décisions prises depuis le Prompt Maître
- 2026-10-16 — Garder le brief complet dans docs/PROJECT_BRIEF.md — pour qu'il voyage avec le code.
- 2026-10-16 — STATE.md fait foi entre sessions — pour éviter de tout relire à chaque reprise.

## Problèmes ouverts / dette technique
- Aucun pour l'instant.

## Prochaine étape (J1)
- Créer le venv et installer opencv-python, numpy, pytesseract, requests, customtkinter.
- Vérifier que Python 3.10+ est disponible.
- Créer le script de test image (charger, taille, gris, sauvegarde).
