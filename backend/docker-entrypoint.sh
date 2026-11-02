#!/bin/sh
set -eu

# Secret Django genere au premier demarrage et conserve dans le volume Docker.
mkdir -p "${CORPUS_DIR:-/data/corpus}"
SECRET_FILE="${CORPUS_DIR:-/data/corpus}/.django_secret_key"
if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
    if [ ! -s "$SECRET_FILE" ]; then
        (umask 077; python -c 'import secrets; print(secrets.token_urlsafe(48))' > "$SECRET_FILE")
    fi
    export DJANGO_SECRET_KEY="$(cat "$SECRET_FILE")"
fi

python manage.py migrate --noinput

# L'API demarre immediatement; le corpus se prepare en tache de fond.
# En cas d'indisponibilite de Gutendex, on retente sans intervention manuelle.
# Les livres deja importes sont conserves dans les volumes nommes.
if [ "${AUTO_IMPORT:-1}" = "1" ]; then
    (
        while ! python manage.py initialize_library --target "${BOOK_TARGET:-1700}"; do
            echo "[initialisation] Import interrompu ; nouvel essai automatique dans 60 s" >&2
            sleep 60
        done
    ) &
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
