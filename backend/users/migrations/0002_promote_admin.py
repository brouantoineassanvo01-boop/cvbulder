"""
Migration autonome pour promouvoir un compte administrateur si les variables
DJANGO_SUPERUSER_* sont fournies.

Le fichier 0001_create_superuser.py a été retiré du working tree. Garder cette
migration autoportée évite de casser le chargement des migrations sur un clone
local tout en restant idempotent.
"""
import os

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_superuser(apps, schema_editor):
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "").strip()
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()

    if not username or not password:
        return

    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"email": email},
    )
    user.email = email or user.email
    user.password = make_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [migrations.RunPython(create_superuser, noop)]
