# Détecteur de spam

Classifieur TF-IDF + Naive Bayes multinomial (97,3 % de justesse en validation).
**Front** React + Tailwind (thème sombre) · **API** FastAPI · déploiement par conteneurs.

```
navigateur ──► front (React, fichiers statiques) ──POST /api/predict──► API FastAPI ──► model.json
```

## Lancer en local

```bash
# API (http://localhost:8000, doc interactive sur /docs)
pip install -r backend/requirements.txt
uvicorn app:app --app-dir backend --reload

# Front (http://localhost:5173, /api est relayé vers le port 8000)
npm install
npm run dev
```

## Docker

```bash
docker compose up --build     # site sur http://localhost:8080, API derrière /api
```

Le conteneur `web` (nginx) sert le site et relaie `/api/` vers `backend`. Chaque image se déploie aussi seule :
`backend/Dockerfile` et `Dockerfile` (front) lisent la variable `PORT` imposée par les hébergeurs.

## Déployer : front sur Vercel, API ailleurs

1. **API** : déployez `backend/` (Dockerfile) sur l'hébergeur de votre choix. Notez son URL, ex. `https://spam-api.onrender.com`.
2. **Vercel** : importez le dépôt (preset Vite détecté) et ajoutez la variable d'environnement
   `VITE_API_URL=https://spam-api.onrender.com` (sans `/` final), puis redéployez.
3. **CORS** : sur l'API, définissez `ALLOWED_ORIGINS=https://votre-site.vercel.app` (plusieurs origines séparées par des virgules ; `*` par défaut).

## API

| Méthode | Route          | Rôle                                                              |
|---------|----------------|-------------------------------------------------------------------|
| GET     | `/api/health`  | Sonde de santé                                                    |
| GET     | `/api/info`    | Justesse, taille d'entraînement, nombre de termes                 |
| POST    | `/api/predict` | Corps `{"text": "..."}` → `{known, label, pSpam, terms[]}`        |

Si aucun terme du message n'est connu du modèle, la réponse est `{"known": false}`.

## Ré-entraîner le modèle

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r srcs/requirements.txt
python3 srcs/get_data.py        # télécharge le dataset
python3 srcs/main.py            # entraîne, écrit srcs/model.joblib
python3 srcs/export_model.py    # convertit en backend/model.json (lu par l'API)
```

L'API lit `model.json` plutôt que le `.joblib` : pas de scikit-learn en production (image légère, démarrage
rapide, pas de problème de version de pickle). Pour Naive Bayes, idf + écart de log-probabilité par terme
suffisent à reproduire `predict_proba` (écart mesuré sur 3 000 messages : < 0,004 %, aucun verdict différent).

## Structure

```
├── backend/          app.py (FastAPI), model.json, Dockerfile, requirements.txt
├── src/              App.jsx, lib/api.js, index.css
├── srcs/             entraînement Python (get_data, main, export_model)
├── Dockerfile, nginx.conf.template, docker-compose.yml
└── index.html, vite.config.js, package.json
```
