"""Authentification JWT qui trace la dernière activité de l'utilisateur.

Chaque appel API authentifié met à jour `cvs.UserActivity.last_seen` (au plus
une écriture par minute et par utilisateur, grâce au cache), ce qui alimente
le compteur « en ligne » du tableau de bord admin.
"""
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication

# Intervalle minimal entre deux écritures pour un même utilisateur.
TOUCH_INTERVAL_SECONDS = 60


def touch_user_activity(user):
    key = f"user-last-seen-{user.pk}"
    if cache.get(key):
        return
    cache.set(key, True, TOUCH_INTERVAL_SECONDS)
    from cvs.models import UserActivity

    UserActivity.objects.update_or_create(user=user, defaults={"last_seen": timezone.now()})


class ActivityJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result:
            try:
                touch_user_activity(result[0])
            except Exception:
                # Le suivi d'activité ne doit jamais faire échouer une requête.
                pass
        return result
