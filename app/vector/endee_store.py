from endee import Endee
from app.vector.embeddings import generate_embeddings


# ==============================
# ENDEE CONFIG
# ==============================

INDEX_NAME = "sentinelai_index"

client = Endee()


# ==============================
# CREATE INDEX
# ==============================

def ensure_index(dim):

    try:

        indexes = client.list_indexes()

        if INDEX_NAME not in indexes:

            client.create_index(
                name=INDEX_NAME,
                dimension=dim,
                space_type="cosine",
                precision="float32"
            )

            print(f"[Endee] Index created: {INDEX_NAME}")

    except Exception as e:

        print("Endee index creation error:", e)


# ==============================
# BUILD VECTOR STORE
# ==============================

def build_endee_store(documents):

    if not documents:
        return {"documents_indexed": 0}

    try:

        print(f"[Endee] Building vector store for {len(documents)} documents")

        embeddings = generate_embeddings(documents)

        dim = len(embeddings[0])

        ensure_index(dim)

        index = client.get_index(name=INDEX_NAME)

        vectors = []

        for i, emb in enumerate(embeddings):

            vectors.append({
                "id": str(i),
                "vector": emb.tolist(),
                "meta": {
                    "text": documents[i]
                }
            })

        # ==============================
        # BATCH UPSERT (1000 limit)
        # ==============================

        BATCH_SIZE = 1000

        for i in range(0, len(vectors), BATCH_SIZE):

            batch = vectors[i:i + BATCH_SIZE]

            print(f"[Endee] Uploading batch {i} → {i + len(batch)}")

            index.upsert(batch)

        print(f"[Endee] Indexed {len(vectors)} vectors")

        return {"documents_indexed": len(vectors)}

    except Exception as e:

        print("Endee build error:", e)

        return {"documents_indexed": 0}


# ==============================
# SEARCH VECTOR STORE
# ==============================

def search_endee(query, top_k=5):

    try:

        query_embedding = generate_embeddings([query])[0]

        index = client.get_index(name=INDEX_NAME)

        results = index.query(
            vector=query_embedding.tolist(),
            top_k=top_k
        )

        documents = []

        for item in results:

            meta = item.get("meta", {})

            if "text" in meta:
                documents.append(meta["text"])

        return documents

    except Exception as e:

        print("Endee search error:", e)

        return []