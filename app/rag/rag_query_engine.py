from app.rag.retriever import build_context
from app.analytics.query_engine import is_analytical_query, run_analytical_query
from app.ai.llm_engine import generate_llm_response


# =================================
# HYBRID RAG + ANALYTICAL ENGINE
# =================================

def rag_query(query: str):
    """
    SentinelAI Hybrid Query Engine
    """

    try:

        # --------------------------------
        # STEP 1 — Analytical Detection
        # --------------------------------

        if is_analytical_query(query):

            analysis_result = run_analytical_query(query)

            if analysis_result and analysis_result.get("type") == "analytical":

                return {
                    "status": "success",
                    "query": query,
                    "engine": "analytical",
                    "answer": analysis_result.get("answer", "No result found."),
                    "context_used": "Analytical engine used",
                    "analysis_data": analysis_result.get("analysis", {})
                }

        # --------------------------------
        # STEP 2 — RAG Retrieval
        # --------------------------------

        context = build_context(query, top_k=5)

        if not context or context.strip() == "":
            context = "No relevant dataset information found."

        # --------------------------------
        # STEP 3 — Prompt Construction
        # --------------------------------

        prompt = f"""
You are an expert business data analyst.

You MUST answer the question ONLY using the dataset rows provided.

DATASET ROWS:
{context}

QUESTION:
{query}

Rules:
- Use the data provided
- Mention numbers when possible
- If the answer cannot be determined from the rows, say:
  "The dataset rows do not contain enough information."
"""

        # --------------------------------
        # STEP 4 — LLM Response
        # --------------------------------

        llm_response = generate_llm_response(prompt)

        return {
            "status": "success",
            "query": query,
            "engine": "rag",
            "context_used": context,
            "answer": llm_response if llm_response else "Unable to generate AI response."
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }