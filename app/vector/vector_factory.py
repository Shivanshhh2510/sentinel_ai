from app.vector.qdrant_store import QdrantStore


def get_vector_store():
    return QdrantStore()