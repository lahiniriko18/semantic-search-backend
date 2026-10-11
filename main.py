import pandas as pd, faiss
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Moteur de recherche sémantique")

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
index = faiss.read_index("data/index.faiss")
df = pd.read_csv("data/clean.csv")

@app.get("/search")
def search(q: str = Query(..., min_length=2), k: int = 5):
    vec = model.encode([q], normalize_embeddings=True)
    scores, ids = index.search(vec, k)
    return [
        {"texte": df.iloc[i]["texte"], "score": round(float(s), 3)}
        for s, i in zip(scores[0], ids[0])
    ]

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/index.html")