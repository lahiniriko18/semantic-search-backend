import pandas as pd, numpy as np, faiss
from sentence_transformers import SentenceTransformer

df = pd.read_csv("data/documents.csv").drop_duplicates("texte")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

emb = model.encode(df["texte"].tolist(), normalize_embeddings=True,
                   show_progress_bar=True)
index = faiss.IndexFlatIP(emb.shape[1])
index.add(emb)

faiss.write_index(index, "data/index.faiss")
df.to_csv("data/clean.csv", index=False)