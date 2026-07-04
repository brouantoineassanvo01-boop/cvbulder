"""
Crée le compte administrateur « Assanvo » au déploiement (accès /admin/).

⚠️ AVANT DE DÉPLOYER : remplace la valeur de SUPERUSER_PASSWORD ci-dessous
(ligne 16) par ton vrai mot de passe. Tant que le placeholder n'est pas
remplacé, la migration ne crée AUCUN compte (sécurité).

APRÈS LE DÉPLOIEMENT : supprime ce fichier puis redéploie. Le compte reste
en base (supprimer le fichier ne supprime pas l'utilisateur), mais le mot de
passe disparaît du code et de GitHub.
"""
from django.contrib.auth.hashers import make_password
from django.db import migrations

SUPERUSER_USERNAME = "Assanvo"
SUPERUSER_PASSWORD = "Assanvo225"  # ← remplace AVANT de déployer
SUPERUSER_EMAIL = "zenovatech001@gmail.com"


def create_superuser(apps, schema_editor):
    if SUPERUSER_PASSWORD == "Assanvo225":
        return
    User = apps.get_model("auth", "User")
    user, _ = User.objects.get_or_create(
        username=SUPERUSER_USERNAME,
        defaults={"email": SUPERUSER_EMAIL},
    )
    user.email = user.email or SUPERUSER_EMAIL
    user.password = make_password(SUPERUSER_PASSWORD)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [migrations.RunPython(create_superuser, noop)]
