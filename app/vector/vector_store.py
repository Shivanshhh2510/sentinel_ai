import faiss
import numpy as np
import pandas as pd
import pickle
import os

from app.vector.embeddings import get_embedding_model


# ==============================
# VECTOR STORE PATHS
# ==============================

INDEX_PATH = "data/vector_index.faiss"
METADATA_PATH = "data/vector_metadata.pkl"


# ==============================
# DATAFRAME → TEXT DOCUMENTS
# ==============================

def dataframe_to_documents(df: pd.DataFrame):

    documents = []

    for _, row in df.iterrows():

        row_text = []

        for col in df.columns:

            value = row[col]

            if pd.isna(value):
                continue

            row_text.append(f"{col}: {value}")

        doc = " | ".join(row_text)

        documents.append(doc)

    return documents


# ==============================
# BUILD VECTOR STORE
# ==============================

def build_vector_store(df: pd.DataFrame):

    os.makedirs("data", exist_ok=True)

    model = get_embedding_model()

    documents = dataframe_to_documents(df)

    if len(documents) == 0:
        raise Exception("No documents generated from dataframe")

    embeddings = model.encode(
        documents,
        convert_to_numpy=True,
        show_progress_bar=True
    ).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(index, INDEX_PATH)

    # Save documents metadata
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(documents, f)

    return {
        "documents_indexed": len(documents),
        "embedding_dimension": dimension
    }


# ==============================
# LOAD VECTOR STORE
# ==============================

def load_vector_store():

    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        return None, None

    index = faiss.read_index(INDEX_PATH)

    with open(METADATA_PATH, "rb") as f:
        documents = pickle.load(f)

    return index, documents


# ==============================
# SEMANTIC SEARCH
# ==============================

def search_vector_store(query: str, top_k: int = 5):

    model = get_embedding_model()

    index, documents = load_vector_store()

    if index is None or documents is None:
        return []

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    results = []

    # FAISS may return -1 or invalid indexes
    for idx in indices[0]:

        if idx == -1:
            continue

        if idx >= len(documents):
            continue

        results.append(documents[idx])

    return results


# ==============================
# ALIAS FOR RETRIEVER
# ==============================

def search_vectors(query: str, top_k: int = 5):
    """
    Alias used by retriever module
    """
    return search_vector_store(query, top_k)