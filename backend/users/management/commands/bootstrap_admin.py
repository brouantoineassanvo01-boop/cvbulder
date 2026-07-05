"""
Crée ou met à jour le compte administrateur depuis les variables d'environnement
DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD / DJANGO_SUPERUSER_EMAIL.

Exécutée à chaque démarrage (start.sh) : idempotente, aucun mot de passe dans
le code. Le mot de passe du compte est TOUJOURS aligné sur la variable — pour
le changer (ou le retrouver après un oubli), modifie la variable sur Render
puis redémarre le service.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée/aligne le compte admin depuis DJANGO_SUPERUSER_USERNAME/PASSWORD/EMAIL."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        if not username or not password:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD non définies : aucun compte créé.")
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Compte admin {'créé' if created else 'mis à jour'} : {username}"))
