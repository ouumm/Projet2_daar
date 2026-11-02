# DAAR — Projet 2 : moteur de recherche d'une bibliothèque

Application : **Vue 3** (frontend), **Django REST** (backend), **PostgreSQL** (base), **Docker Compose**.

## Démarrage : une seule commande

Installer et lancer Docker Desktop, décompresser le ZIP, ouvrir un terminal dans ce dossier puis :

```bash
docker compose up
```

La commande lance les 3 services, exécute les migrations Django, puis démarre automatiquement
l'import Gutenberg, la création de l'index et le graphe de Jaccard.
L'application est accessible à **http://localhost:8080** (ou autre port `APP_PORT`).

**Important :** l'interface démarre avant la fin de l'import. Pendant l'initialisation,
les recherches peuvent avoir des résultats absents ou incomplets.
L'import nécessite Internet et le téléchargement de milliers de textes ; il peut échouer
si une source distante est indisponible. Désormais, les requêtes HTTP sont retentées,
et l'import est relancé automatiquement en cas de problème réseau temporaire :
**pas de commande manuelle d'import à exécuter**. Si Gutendex reste inaccessible,
l'API et l'interface peuvent s'ouvrir, mais la bibliothèque restera vide ou incomplète.
Vérifier les logs `backend` et les effectifs réellement importés avant d'affirmer
que le projet respecte le seuil demandé.

## .env et .env_exemple

- `.env` : configuration locale **avec vrai mot de passe** PostgreSQL et clé Django ;
  **NE PAS envoyer sur GitLab/Moodle** ni partager publiquement.
- `.env_exemple` : variables utiles et **valeurs fictives** ; à conserver dans le rendu.
- `docker compose up` **marche aussi sans `.env`** : les valeurs par défaut sont appliquées.
  Dans ce cas **uniquement**, PostgreSQL est configuré en `trust` sur le réseau Docker
  interne `db_net` (acceptable pour une démonstration locale, **pas en production**).
- Quand `.env` est présent, PostgreSQL utilise `scram-sha-256` avec `DB_PASSWORD`.
  Si `pgdata` a déjà été initialisé dans un mode différent, ne pas simplement changer
  de méthode d'authentification : un changement de mot de passe côté base peut être
  nécessaire. Pour un environnement de test sans données à préserver, `docker compose down -v`
  puis `docker compose up` recrée une base vierge (**attention : -v supprime les données**).
- Les Dockerfiles ne contiennent aucun mot de passe ni aucune clé.

## Architecture

- Frontend et backend communiquent par `app_net`.
- Le backend communique avec PostgreSQL par `db_net` (réseau interne).
- Le frontend expose le port 8080 vers le navigateur ; la base n'expose pas de port hôte.
- Le volume nommé `pgdata` conserve la base ; `corpus` conserve les textes et fichiers
  internes d'initialisation. Aucun dossier local n'est monté en bind mount.
- Nginx relaie `/api/` vers le backend.

## Vérifications (une fois les services lancés)

```bash
docker compose ps
docker compose exec backend python manage.py test
docker compose exec backend python manage.py shell -c "from books.models import Book; print('livres=', Book.objects.count(), 'invalides=', Book.objects.filter(word_count__lt=10000).count())"
docker compose logs --tail=50 backend
```

Vérifier également le moteur dans `http://localhost:8080`, l'accessibilité de
l'application depuis au moins **2 machines clientes**, et les performances.

## API

- `GET /api/books/` : liste des livres.
- `GET /api/book/<id>/` : détails.
- `GET /api/search/?q=mot&mode=exact|contains&rank=occurrences|pagerank|closeness` : recherche.
- `GET /api/search/advanced/?regex=...&scope=index|content` : RegEx.
- `POST /api/book/<id>/click/` : nombre de clics.
- `GET /api/book/<id>/text/?n=3000` : extrait.

## Statut / limites

- L'exécution réelle de Docker, les pipelines GitLab et les tests Django ne sont pas
  vérifiés dans cette archive ; ils nécessitent un environnement opérationnel.
- La recherche RegEx utilise toujours `re` de Python ; l'automate Java du projet 1
  **n'a pas encore été intégré**.
- Le corpus de 1700 livres n'est **pas inclus** dans le ZIP ; l'import se fait
  automatiquement au démarrage (objectif minimal du sujet : 1664 livres de 10000 mots).
- Kubernetes/CKA, Databricks, ML Zoomcamp et MLOps Zoomcamp ne figurent pas parmi
  les exigences identifiées dans l'énoncé écrit du projet 2.

Voir `TODO_PROJET2.md` pour le plan de finalisation.

## Si Gutendex est lent ou inaccessible

Le message `ReadTimeout: gutendex.com` indique un délai d'attente lors de l'import,
**pas un problème Docker ni PostgreSQL**. Le backend réessaie désormais les pages
plusieurs fois, puis relance l'initialisation dans 60 secondes si nécessaire.
Les livres déjà enregistrés restent présents dans le volume `corpus` et la base.

Pour appliquer cette correction sur une installation où les images sont déjà créées :

```bash
docker compose up --build
```

Cela reconstruit les images et lance l'application en une seule commande. Pour les
prochains démarrages, `docker compose up` suffit. Ne pas utiliser `docker compose
down -v` pendant un dépannage d'import : cette option efface les données.

Pour vérifier l'avancement sans interrompre le démarrage :

```bash
docker compose logs -f backend
```
