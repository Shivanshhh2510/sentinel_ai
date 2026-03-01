from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.rag_query_engine import rag_query

router = APIRouter()


# ===========================
# Request Schema
# ===========================

class QueryRequest(BaseModel):
    query: str


# ===========================
# RAG Query Endpoint
# ===========================

@router.post("/rag/query")
def query_rag(request: QueryRequest):

    try:

        result = rag_query(request.query)

        return {
            "status": "success",
            "query": result["query"],
            "answer": result["answer"],
            "context_used": result["context_used"]
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }