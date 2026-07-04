#!/bin/sh
set -eu

mkdir -p "${DJANGO_MEDIA_ROOT:-/app/media}"

python manage.py migrate --noinput

# Reseed si le catalogue public n'existe pas en base OU si ses aperçus ne sont
# plus réellement présents sur le disque persistant.
# En ARRIÈRE-PLAN : le seed rend 21 aperçus WeasyPrint (plusieurs minutes sur
# un petit CPU) et ne doit jamais retarder l'ouverture du port, sinon le
# health check Render échoue et l'API reste injoignable.
needs_seed_catalog() {
    python manage.py shell -c '
from templates.models import CVTemplate
from templates.management.commands.seed_catalog import CATALOG

expected_slugs = [slug for slug, *_ in CATALOG]
templates = {
    template.slug: template
    for template in CVTemplate.objects.filter(is_active=True, slug__in=expected_slugs)
}

if len(templates) != len(expected_slugs):
    raise SystemExit(1)

for slug in expected_slugs:
    template = templates.get(slug)
    field = getattr(template, "preview_full", None)
    name = getattr(field, "name", "")
    if not name:
        raise SystemExit(1)
    try:
        if not field.storage.exists(name):
            raise SystemExit(1)
    except Exception:
        raise SystemExit(1)

raise SystemExit(0)
'
}

if ! needs_seed_catalog; then
    (python manage.py seed_catalog || echo "seed_catalog a échoué (l'API reste fonctionnelle)") &
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile -
