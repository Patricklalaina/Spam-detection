"""Exporte srcs/model.joblib vers backend/model.json, lu par l'API.

Pour Naive Bayes multinomial + tf-idf, la prédiction se réduit à :
    score = biais + somme_over_termes( tfidf_normalisé(terme) * delta(terme) )
avec delta = log P(terme|spam) - log P(terme|sain). Il suffit donc de sauvegarder,
pour chaque terme, son idf et son delta. Aucune dépendance scikit-learn côté API.
"""
import json
from pathlib import Path

import joblib

SRC = Path(__file__).parent / 'model.joblib'
DST = Path(__file__).parent.parent / 'backend' / 'model.json'


def main() -> None:
    bundle = joblib.load(SRC)
    tfidf, model = bundle['vectorizer'], bundle['model']
    assert list(model.classes_) == [0, 1]

    vocab = tfidf.vocabulary_
    mots = sorted(vocab, key=vocab.get)  # dans l'ordre des colonnes
    delta = model.feature_log_prob_[1] - model.feature_log_prob_[0]
    biais = model.class_log_prior_[1] - model.class_log_prior_[0]

    payload = {
        'vocab': mots,
        'idf': [round(float(x), 4) for x in tfidf.idf_],
        'delta': [round(float(x), 4) for x in delta],
        'bias': round(float(biais), 6),
        'accuracy': float(bundle['accuracy']),
        'nTrain': int(bundle['n_train']),
    }
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(payload, separators=(',', ':'), ensure_ascii=False), encoding='utf-8')
    print(f"[✓] {len(mots)} termes exportés -> {DST} ({DST.stat().st_size / 1e6:.1f} Mo)")


if __name__ == '__main__':
    main()
