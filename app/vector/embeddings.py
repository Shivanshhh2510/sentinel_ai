from sentence_transformers import SentenceTransformer
import numpy as np

# ==============================
# LOAD EMBEDDING MODEL (ONLY ONCE)
# ==============================

_embedding_model = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    return _embedding_model


# ==============================
# ROW → TEXT CONVERSION
# ==============================

def row_to_text(row):

    text_parts = []

    for col, value in row.items():

        if value is None:
            continue

        text_parts.append(f"{col}: {value}")

    return ", ".join(text_parts)


# ==============================
# GENERATE EMBEDDINGS
# ==============================

def generate_embeddings(texts):

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings