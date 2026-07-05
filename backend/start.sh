#!/bin/sh
set -eu

mkdir -p "${DJANGO_MEDIA_ROOT:-/app/media}"

python manage.py migrate --noinput

# Compte admin : créé/aligné à chaque démarrage depuis DJANGO_SUPERUSER_*
# (variables Render). Mot de passe oublié => changer la variable + redémarrer.
python manage.py bootstrap_admin || echo "bootstrap_admin a échoué (le démarrage continue)"

# Reseed uniquement si le catalogue en BASE est incomplet (nouveau modèle,
# première installation). PAS de vérification des fichiers d'aperçu : sur les
# hébergements sans disque persistant (plan Free), le dossier media disparaît
# à CHAQUE réveil — vérifier les fichiers relançait le seed complet (21 rendus
# WeasyPrint, plusieurs minutes de CPU) à chaque redémarrage. L'affichage des
# aperçus est garanti par les fichiers STATIQUES embarqués dans l'image
# (backend/static/templates/previews/) via le repli de CVTemplate.preview_url.
# En ARRIÈRE-PLAN : le seed ne doit jamais retarder l'ouverture du port, sinon
# le health check Render échoue et l'API reste injoignable.
catalog_complete() {
    python manage.py shell -c '
from templates.models import CVTemplate
from templates.management.commands.seed_catalog import CATALOG

expected_slugs = [slug for slug, *_ in CATALOG]
active = CVTemplate.objects.filter(is_active=True, slug__in=expected_slugs).count()
raise SystemExit(0 if active == len(expected_slugs) else 1)
'
}

if ! catalog_complete; then
    (python manage.py seed_catalog || echo "seed_catalog a échoué (l'API reste fonctionnelle)") &
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile -
