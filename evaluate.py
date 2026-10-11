tests = [("voiture rapide", 12), ("recette de cuisine", 45)]  # (requête, id attendu)
ok = 0
for requete, attendu in tests:
    vec = model.encode([requete], normalize_embeddings=True)
    _, ids = index.search(vec, 5)
    ok += attendu in ids[0]
print(f"Top-5 : {ok}/{len(tests)}")
