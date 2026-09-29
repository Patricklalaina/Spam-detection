from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from scipy.sparse import spmatrix
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt


DATA_PATH = Path(__file__).parent / 'data.csv'
MODEL_PATH = Path(__file__).parent / 'model.joblib'


def transform_data(x_train: np.ndarray, x_val: np.ndarray) -> tuple[spmatrix, spmatrix, TfidfVectorizer]:
    # Fit on the training set only, so the validation set stays unseen
    tfidf = TfidfVectorizer()
    x_train_vec = tfidf.fit_transform(x_train)
    x_val_vec = tfidf.transform(x_val)
    return x_train_vec, x_val_vec, tfidf

def main() -> None:

    """format
    label,text
    1,do you feel the pressure to perform and not rising to the occasion try v ia gr a your anxiety will be a thing of the past and you will be back to your old self
    """
    df = pd.read_csv(DATA_PATH)
    # to_numpy(dtype=object) plutôt que .values : avec pyarrow installé, pandas
    # renvoie un tableau Arrow que scikit-learn ne sait pas indexer.
    y = df['label'].to_numpy()
    X = df['text'].to_numpy(dtype=object)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    X_train_vec, X_val_vec, tfidf = transform_data(X_train, X_val)

    model = MultinomialNB()

    model.fit(X_train_vec, y_train)

    y_predict = model.predict(X_val_vec)
    print(classification_report(y_val, y_predict, digits=4))
    conf_matrix = confusion_matrix(y_val, y_predict)

    # Le vectoriseur et le modèle doivent rester ensemble : le modèle attend
    # exactement le vocabulaire appris par ce vectoriseur.
    joblib.dump(
        {
            'vectorizer': tfidf,
            'model': model,
            'accuracy': accuracy_score(y_val, y_predict),
            'n_train': X_train.shape[0],
            'n_val': X_val.shape[0],
        },
        MODEL_PATH,
    )
    print(f"[✓] Modèle sauvegardé : {MODEL_PATH}")

    display = ConfusionMatrixDisplay(confusion_matrix=conf_matrix,display_labels=['Not Spam', 'Spam'])
    display.plot(cmap=plt.cm.Blues)
    plt.title("Matrice de Confusion - Naive Bayes")
    plt.xlabel("Classes Prédites")
    plt.ylabel("Classes Réelles")
    plt.show()

if __name__=='__main__':
    main()
