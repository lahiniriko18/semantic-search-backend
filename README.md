# Moteur de recherche sémantique : Backend

API **FastAPI** d'un moteur de recherche sémantique en français, réalisé pour un projet scolaire sur les **embeddings**.

L'utilisateur envoie une recherche en langage naturel (ex. « automobile propre ») et l'API renvoie les documents dont le **sens** est le plus proche, même s'ils ne contiennent pas les mêmes mots (ex. « La voiture électrique permet de rouler sans polluer... »).

> Le frontend (Next.js) est dans un dépôt séparé : _(lien du dépôt frontend)_

## Comment ça marche

```
documents.csv ──▶ modèle d'embedding ──▶ vecteurs ──▶ index FAISS
                                                          │
requête ──▶ modèle d'embedding ──▶ vecteur ──▶ recherche ─┘──▶ top k documents
```

1. Les documents sont transformés en vecteurs par le modèle `paraphrase-multilingual-MiniLM-L12-v2`.
2. Les vecteurs sont stockés dans un index **FAISS** (calculé une seule fois).
3. À chaque recherche, la requête est transformée en vecteur avec le même modèle.
4. FAISS renvoie les documents les plus proches (similarité cosinus).

## Structure du projet

```
.
├── data/
│   ├── documents.csv       # corpus de départ (colonnes : id, texte)
│   ├── clean.csv           # généré par build_index.py
│   └── index.faiss         # généré par build_index.py
├── build_index.py          # crée les embeddings et l'index
├── main.py                 # API FastAPI
├── evaluate.py             # évaluation (top-5)
├── requirements.txt
└── README.md
```

## Prérequis

- Python 3.10 ou plus récent
- Une connexion internet **au premier lancement** (téléchargement du modèle, environ 470 Mo)

## Installation

### 1. Créer l'environnement virtuel

Créez-le de préférence sur votre disque principal (les disques externes NTFS/exFAT ne gèrent pas bien les venv) :

```bash
python3 -m venv ~/venvs/semantic-search
source ~/venvs/semantic-search/bin/activate      # Windows : venv\Scripts\activate
```

Vérifiez que `python` et `pip` pointent bien vers le venv :

```bash
which python
which pip
```

### 2. Installer les dépendances

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

L'installation de PyTorch en version CPU évite de télécharger plusieurs Go de bibliothèques CUDA inutiles sans carte graphique NVIDIA.

Contenu de `requirements.txt` :

```
sentence-transformers
faiss-cpu
fastapi
uvicorn
pandas
numpy
```

### 3. Préparer les données

Le fichier `data/documents.csv` doit contenir une colonne `texte` (une ligne par document). Un corpus d'exemple de 50 documents est fourni.

### 4. Construire l'index (une seule fois)

```bash
python build_index.py
```

Le premier lancement télécharge le modèle d'embedding (internet nécessaire). Il est ensuite gardé en cache dans `~/.cache/huggingface/`. Le script génère `data/index.faiss` et `data/clean.csv`.

À relancer chaque fois que `documents.csv` change.

## Lancer l'API

```bash
uvicorn main:app --reload
```

- API : http://127.0.0.1:8000
- Documentation interactive (Swagger) : http://127.0.0.1:8000/docs

## Documentation de l'API

### `GET /search`

| Paramètre | Description                                 | Défaut      |
| --------- | ------------------------------------------- | ----------- |
| `q`       | Requête de recherche (minimum 2 caractères) | obligatoire |
| `k`       | Nombre de résultats à renvoyer              | 5           |

Exemple :

```bash
curl "http://127.0.0.1:8000/search?q=automobile%20propre&k=3"
```

Réponse :

```json
[
  {
    "texte": "La voiture électrique permet de rouler sans émettre de gaz polluants...",
    "score": 0.642
  },
  {
    "texte": "Le moteur à explosion transforme l'énergie du carburant...",
    "score": 0.431
  }
]
```

Le score est une similarité cosinus : plus il est proche de 1, plus le document est pertinent.

Une requête de moins de 2 caractères renvoie une erreur `422`.

## CORS

Le frontend tourne sur un autre port (et un autre dépôt), donc `main.py` doit autoriser son origine :

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

Si le frontend est déployé ailleurs, ajoutez son URL dans `allow_origins`.

## Évaluation

```bash
python evaluate.py
```

Mesure combien de requêtes de test retrouvent le bon document dans le top 5. Comparez le résultat avec une recherche par mots-clés pour montrer l'intérêt des embeddings.

Exemples de requêtes à tester :

| Requête                                   | Document attendu                  |
| ----------------------------------------- | --------------------------------- |
| automobile propre                         | voiture électrique                |
| comment faire une pâte à pizza            | recette de pizza                  |
| protéger la planète                       | recyclage, énergies renouvelables |
| animal de compagnie qui miaule            | chat                              |
| apprendre à une machine                   | apprentissage automatique         |
| pays de l'océan Indien avec des lémuriens | Madagascar                        |

## Mode hors ligne

Une fois le modèle en cache, vous pouvez travailler sans internet :

```bash
HF_HUB_OFFLINE=1 uvicorn main:app --reload
```

## Problèmes fréquents

| Problème                                     | Solution                                                                                                            |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `error: externally-managed-environment`      | Vous n'êtes pas dans un venv. Créez-en un et activez-le.                                                            |
| `ModuleNotFoundError: sentence_transformers` | Le venv n'est pas activé, ou les paquets sont installés dans un autre Python. Utilisez `python -m pip install ...`. |
| `FileNotFoundError: data/index.faiss`        | Lancez d'abord `python build_index.py`.                                                                             |
| Erreur CORS dans le navigateur               | Vérifiez le middleware CORS dans `main.py`.                                                                         |
| Téléchargement du modèle très lent           | Laissez finir, ou copiez le dossier `~/.cache/huggingface/` depuis une autre machine.                               |
| Avertissement « NVIDIA driver too old »      | Sans importance, le calcul se fait sur CPU.                                                                         |

## Technologies

Python, FastAPI, sentence-transformers, FAISS, pandas, modèle `paraphrase-multilingual-MiniLM-L12-v2`.

## Auteurs

Projet réalisé par : _(noms de l'équipe)_
