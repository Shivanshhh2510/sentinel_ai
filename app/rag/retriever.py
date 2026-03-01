from app.vector.endee_store import search_endee


# ==============================
# RETRIEVE RELEVANT DOCUMENTS
# ==============================

def retrieve_relevant_rows(query: str, top_k: int = 5):
    """
    Retrieve relevant dataset rows using Endee vector database.
    """

    try:

        results = search_endee(query, top_k)

        if not results:
            return []

        # Ensure results are strings
        cleaned_results = []

        for r in results:
            if r is None:
                continue
            cleaned_results.append(str(r))

        return cleaned_results

    except Exception as e:

        print("[Retriever Error]:", e)

        return []


# ==============================
# BUILD CONTEXT FOR LLM
# ==============================

def build_context(query: str, top_k: int = 5):
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