from pathlib import Path
import requests
from tqdm import tqdm
import sys


DATA_PATH = Path(__file__).parent / 'data.csv'

url = 'https://raw.githubusercontent.com/PuruSinghvi/Spam-Email-Classifier/refs/heads/main/Datasets/email_text.csv'
response = requests.get(url=url, stream=True)


if response.status_code == 200:
    total_size = int(response.headers.get('content-length', 0))

    progress_bar = tqdm(
        total=total_size, 
        unit='o',             # Unité en octets
        unit_scale=True,      # Conversion automatique en Ko, Mo, etc.
        unit_divisor=1024,
        desc="* Téléchargement", 
        colour="#00FF00",     # Couleur de la barre (vert fluo)
        bar_format="{l_bar}{bar:40}{r_bar}" # Style de la barre
    )
    with open(DATA_PATH, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
                
    progress_bar.close()
    print("\n[✓] Téléchargement terminé avec succès !")

else:
    sys.stderr.writelines(f"Error code: {response.status_code}")
    sys.exit(1)