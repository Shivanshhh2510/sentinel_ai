import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.vector.base import BaseVectorStore
from app.vector.embeddings import get_embedding_model


class QdrantStore(BaseVectorStore):

    def __init__(self):
        self.collection_name = "sentinelai_vectors"

        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")

        self.client = QdrantClient(url=qdrant_url)

        self.model = get_embedding_model()

        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            names = [c.name for c in collections]

            if self.collection_name not in names:

                # temporary embedding dimension detection
                test_vector = self.model.encode(["test"])[0]
                dimension = len(test_vector)

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE
                    )
                )

                print("[Qdrant] Collection created")

        except Exception as e:
            print("[Qdrant] Collection init error:", e)

    def upsert(self, documents: List[str]) -> dict:

        if not documents:
            return {"documents_indexed": 0}

        embeddings = self.model.encode(documents)

        BATCH_SIZE = 500  # safe batch size
        total_indexed = 0

        for start in range(0, len(embeddings), BATCH_SIZE):

            end = start + BATCH_SIZE
            batch_vectors = embeddings[start:end]
            batch_docs = documents[start:end]

            points = []

            for idx, vector in enumerate(batch_vectors):
                global_id = start + idx  # ensure unique ID

                points.append(
                    PointStruct(
                        id=global_id,
                        vector=vector.tolist(),
                        payload={"text": batch_docs[idx]}
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            total_indexed += len(points)

            print(f"[Qdrant] Indexed batch {start} → {end}")

        return {"documents_indexed": total_indexed}

    def search(self, query: str, top_k: int = 5) -> List[str]:

        query_vector = self.model.encode([query])[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            limit=top_k
        )

        documents = []

        if results and results.points:
            for point in results.points:
                if point.payload and "text" in point.payload:
                    documents.append(point.payload["text"])

        return documents