# Checklist Projet 2 DAAR — à valider avant le 22/11/2026

`[x]` = présent dans le code/configuration ; `[ ]` = à tester, compléter ou justifier.

## P0 — faire fonctionner le projet

- [x] Frontend Vue, backend Django REST et PostgreSQL présents.
- [x] Dockerfiles frontend/backend, fichier `docker-compose.yml`.
- [x] Réseaux Docker `app_net` (front/back) et `db_net` interne (back/DB).
- [x] Volumes nommés `pgdata` (base) et `corpus` (textes) ; sans bind mounts.
- [x] `.env` local, `.env_exemple`, exclusion de `.env` par `.gitignore`.
- [x] Migrations, lancement serveur et initialisation planifiés automatiquement.
- [ ] **Toi :** lancer `docker compose up` depuis le dossier ; vérifier qu'aucun conteneur n'échoue.
- [ ] **Toi :** tester `http://localhost:8080` et les endpoints API depuis un navigateur.
- [ ] **Ensemble :** valider les logs et les étapes automatiques import → index → graphe.
- [ ] **Toi :** vérifier le fonctionnement depuis 2 machines clientes pour la démonstration.

## P1 — exigences fonctionnelles du sujet

- [x] Script Gutenberg avec filtre `>= 10000` mots et objectif de 1700 livres.
- [ ] **Toi :** vérifier en base les **1664 livres minimum**, chacun d'au moins **10000 mots**.
- [x] Recherche par mot-clef et index inversé présents dans le code.
- [x] Recherche avancée RegEx (moteur Python `re`) présente.
- [x] Classement par occurrences, PageRank et closeness présent.
- [x] Graphe de Jaccard et suggestions présents.
- [ ] **Ensemble :** prouver les résultats sur des livres réels ; comparer les classements.
- [ ] **Moi :** si retenu, adapter l'automate Java RegEx du projet 1 et ajouter des tests de compatibilité. **Facultatif** pour l'énoncé.
- [ ] **Ensemble :** vérifier les performances sur 1664+ livres (import, index, recherche et graphe).

## P2 — qualité et livraison

- [x] Tests unitaires KMP, API et classement présents.
- [ ] **Toi :** exécuter `docker compose exec backend python manage.py test`, garder la preuve.
- [ ] **Moi :** compléter les cas limites et tests de régression si besoin.
- [x] Fichier `.gitlab-ci.yml` présent.
- [ ] **Toi :** créer/pousser le dépôt GitLab, vérifier le lien et le pipeline vert.
- [ ] **Ensemble :** documenter les choix algorithmiques (KMP, RegEx, Jaccard, PageRank/closeness), structures et complexités.
- [ ] **Ensemble :** réaliser tests de charge/pertinence et graphiques de performance.
- [ ] **Moi :** aider à rédiger un rapport de 10–15 pages (12 pages recommandées) avec sources des textes.
- [ ] **Toi/groupe :** préparer une présentation orale de 20 min ou vidéo pitch ~5 min, avec démo.
- [ ] **Toi :** préparer l'archive nommée avec les noms du groupe, **<30 Mo**, sans `.env` réel ni corpus, puis déposer sur Moodle.

## Échéances de l'énoncé

- **16 novembre 2026** : oral (si choix présentation orale).
- **22 novembre 2026 à 23 h 59** : archive finale sur Moodle (avec vidéo si ce mode est choisi).

## Hors périmètre de l'énoncé PDF reçu (à clarifier si consigne orale)

- Kubernetes / CKA
- Databricks
- ML Zoomcamp / MLOps Zoomcamp

### Correction réseau du 02/11/2026

- [x] Requêtes HTTP Gutendex avec tentatives supplémentaires et délai de lecture adapté.
- [x] Relance automatique du processus d'import après un échec réseau.
- [x] Tests unitaires du mécanisme de retry ajoutés.
- [ ] Tester `docker compose up --build` sur Mac et vérifier la reprise dans les logs.
- [ ] Vérifier que 1700 livres d'au moins 10000 mots sont réellement importés.
