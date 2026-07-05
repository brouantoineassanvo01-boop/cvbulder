"""
Rejoue la création/promotion du compte administrateur.

Nécessaire car la migration 0001 a déjà été enregistrée comme appliquée en
production alors que sa condition de garde l'avait rendue inopérante —
Django ne rejoue jamais une migration déjà appliquée. Cette migration
réutilise le nom, l'email et le MOT DE PASSE définis dans 0001 : rien à
re-saisir ici.

APRÈS LE DÉPLOIEMENT : supprime ce fichier ET 0001_create_superuser.py,
puis redéploie. Le compte admin reste en base.
"""
from importlib import import_module

from django.db import migrations

_first = import_module("users.migrations.0001_create_superuser")


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_create_superuser"),
    ]

    operations = [migrations.RunPython(_first.create_superuser, _first.noop)]
