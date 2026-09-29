"""API du détecteur de spam (FastAPI).

Le modèle est lu depuis model.json (produit par srcs/export_model.py) : pas de scikit-learn
en production, donc une image légère, un démarrage rapide et aucun souci de version de pickle.
"""
import json
import os
import re
from collections import Counter
from math import exp, sqrt
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MODEL = json.loads((Path(__file__).parent / 'model.json').read_text(encoding='utf-8'))
VOCAB, IDF, DELTA, BIAS = MODEL['vocab'], MODEL['idf'], MODEL['delta'], MODEL['bias']
INDEX = {mot: i for i, mot in enumerate(VOCAB)}
TOKEN = re.compile(r'(?u)\b\w\w+\b')  # tokenisation par défaut de TfidfVectorizer

app = FastAPI(title='Spam classifier API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv('ALLOWED_ORIGINS', '*').split(',') if o.strip()],
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=50_000)


def analyser(text: str, k: int = 6) -> dict:
    comptes = Counter(m for m in TOKEN.findall(text.lower()) if m in INDEX)
    if not comptes:
        return {'known': False}

    poids = {INDEX[m]: n * IDF[INDEX[m]] for m, n in comptes.items()}
    norme = sqrt(sum(w * w for w in poids.values()))
    apports = {i: (w / norme) * DELTA[i] for i, w in poids.items()}

    score = max(-700.0, min(700.0, BIAS + sum(apports.values())))
    p_spam = 1 / (1 + exp(-score))
    top = sorted(apports.items(), key=lambda kv: -abs(kv[1]))[:k]
    return {
        'known': True,
        'label': 'spam' if p_spam >= 0.5 else 'ham',
        'pSpam': p_spam,
        'terms': [{'word': VOCAB[i], 'weight': w} for i, w in top],
    }


@app.get('/api/health')
def health() -> dict:
    return {'status': 'ok'}


@app.get('/api/info')
def info() -> dict:
    return {'accuracy': MODEL['accuracy'], 'nTrain': MODEL['nTrain'], 'nTerms': len(VOCAB)}


@app.post('/api/predict')
def predict(msg: Message) -> dict:
    return analyser(msg.text)
