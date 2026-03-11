from app.vector.vector_factory import get_vector_store


# ==============================
# RETRIEVE RELEVANT DOCUMENTS
# ==============================

def retrieve_relevant_rows(query: str, top_k: int = 20):
    """
    Retrieve relevant dataset rows using VectorStore abstraction (Qdrant).
    """

    try:
        vector_store = get_vector_store()

        results = vector_store.search(query, top_k)

        if not results:
            return []

        cleaned_results = []

        for r in results:

            if r is None:
                continue

            text = str(r).strip()

            if text == "":
                continue

            cleaned_results.append(text)

        return cleaned_results

    except Exception as e:
        print("[Retriever Error]:", e)
        return []


# ==============================
# BUILD CONTEXT FOR LLM
# ==============================

def build_context(query: str, top_k: int = 20):
    """
    Build textual context for the LLM using retrieved rows.
    """

    rows = retrieve_relevant_rows(query, top_k)

    if not rows:
        return "No relevant dataset information found."

    context_parts = []

    for i, row in enumerate(rows):
        context_parts.append(f"Row {i+1}: {row}")

    context = "\n".join(context_parts)

    return context