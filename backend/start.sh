#!/bin/sh
set -eu

mkdir -p "${DJANGO_MEDIA_ROOT:-/app/media}"

python manage.py migrate --noinput

# Reseed si le catalogue est vide OU si le modèle vedette n'existe pas encore
# (permet de déployer un nouveau catalogue sans intervention manuelle).
if ! python manage.py shell -c "from templates.models import CVTemplate; raise SystemExit(0 if CVTemplate.objects.filter(is_active=True, slug='prestige-orange').exists() else 1)"; then
    python manage.py seed_catalog
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile -
