#!/bin/sh
set -eu

mkdir -p "${DJANGO_MEDIA_ROOT:-/app/media}"

python manage.py migrate --noinput

# Reseed si le catalogue est vide OU si le modèle vedette n'existe pas encore
# (permet de déployer un nouveau catalogue sans intervention manuelle).
# En ARRIÈRE-PLAN : le seed rend 21 aperçus WeasyPrint (plusieurs minutes sur
# un petit CPU) et ne doit jamais retarder l'ouverture du port, sinon le
# health check Render échoue et l'API reste injoignable.
if ! python manage.py shell -c "from templates.models import CVTemplate; raise SystemExit(0 if CVTemplate.objects.filter(is_active=True, slug='prestige-orange').exists() else 1)"; then
    (python manage.py seed_catalog || echo "seed_catalog a échoué (l'API reste fonctionnelle)") &
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile -
