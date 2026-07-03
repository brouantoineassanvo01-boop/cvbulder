# Deploiement CVBuilder

## Architecture recommandee

| Partie | Ou | Comment |
|--------|-----|---------|
| Frontend React/Vite | Render Static Site | via `render.yaml` |
| Backend Django | Render Web Service (Docker) | via `backend/Dockerfile` |
| Base de donnees | Render Postgres | via `DATABASE_URL` |
| Fichiers media | Render Persistent Disk | monte sur `/app/media` |

Le backend utilise WeasyPrint, LibreOffice, Tesseract, Poppler et OpenCV. Il doit rester sur une plateforme conteneurisee comme Render.

## Deploiement complet sur Render

1. Pousse le repo sur GitHub.
2. Dans Render, ouvre `New +` puis `Blueprint`.
3. Selectionne le repo `Assanvobrou/cvbuilder`.
4. Render lit `render.yaml` et cree :
   - `cvbuilder-web` pour le frontend
   - `cvbuilder-api` pour le backend
   - `cvbuilder-db` pour Postgres
5. Renseigne uniquement les secrets demandes :
   - `GROQ_API_KEY`
   - `PAYSTACK_SECRET_KEY`
   - `PAYSTACK_PUBLIC_KEY`
6. Lance le deploy.

## Ce qui est maintenant automatique

- `VITE_API_URL` pointe automatiquement vers l'URL publique du backend Render.
- `DJANGO_ALLOWED_HOSTS` se cale sur le hostname public du backend.
- `FRONTEND_URL` se cale sur l'URL publique du frontend.
- `PAYSTACK_CALLBACK_URL` tombe par defaut sur `FRONTEND_URL/dashboard`.
- Le backend sert les fichiers `media/` meme avec `DEBUG=false`.
- Au premier boot, le conteneur :
  - lance les migrations
  - initialise le catalogue de templates si la base est vide
  - demarre Gunicorn

## Verifications apres deploy

1. Ouvre l'URL du frontend Render et verifie que la galerie s'affiche.
2. Ouvre `https://.../api/templates/` sur le backend et verifie que l'API renvoie des templates.
3. Cree un compte test depuis le frontend.
4. Depuis Render > `cvbuilder-api` > `Shell`, cree l'admin :

```bash
python manage.py createsuperuser
```

## Paystack

Dans Paystack, configure le webhook sur :

```text
https://TON_BACKEND_RENDER/api/cvs/payments/paystack-webhook/
```

Si tu utilises un domaine custom pour le frontend, pense aussi a mettre a jour :

- `FRONTEND_URL`
- `DJANGO_CORS_ORIGINS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- eventuellement `PAYSTACK_CALLBACK_URL`

## Variables backend utiles

| Variable | Exemple | Role |
|----------|---------|------|
| `DJANGO_DEBUG` | `false` | mode prod |
| `DJANGO_SECRET_KEY` | generee par Render | secret Django |
| `DJANGO_ALLOWED_HOSTS` | `cvbuilder-api.onrender.com` | hosts backend |
| `FRONTEND_URL` | `https://cvbuilder-web.onrender.com` | URL du frontend |
| `DATABASE_URL` | `postgres://...` | Postgres Render |
| `DJANGO_MEDIA_ROOT` | `/app/media` | disque persistant |
| `DJANGO_SERVE_MEDIA` | `true` | sert previews/photos en prod |
| `AI_PROVIDER` | `groq` | fournisseur IA |
| `GROQ_API_KEY` | `gsk_...` | secret IA |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | modele IA |
| `GROQ_TPM_LIMIT` | `7600` | marge sur le quota gratuit |
| `PAYSTACK_SECRET_KEY` | `sk_live_...` | secret paiement |
| `PAYSTACK_PUBLIC_KEY` | `pk_live_...` | cle publique paiement |
| `PAYSTACK_CURRENCY` | `XOF` | devise |
| `PAYSTACK_CALLBACK_URL` | `https://frontend.onrender.com/dashboard` | retour apres paiement |
