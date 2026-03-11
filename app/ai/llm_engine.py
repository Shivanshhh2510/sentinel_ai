from app.llm.llm_factory import get_llm


# ==========================================
# FALLBACK ML EXPLANATION
# ==========================================

def fallback_explanation(prediction, confidence, top_features):

    feature_text = ", ".join(top_features) if top_features else "multiple dataset features"

    return (
        f"The model predicts '{prediction}' with "
        f"{round(confidence * 100, 2)}% confidence. "
        f"This decision is mainly influenced by: {feature_text}."
    )


# ==========================================
# FALLBACK RAG RESPONSE
# ==========================================

def fallback_rag_response(prompt: str):

    return (
        "AI reasoning service is currently unavailable. "
        "Insights can still be derived from charts and dataset analysis."
    )


# ==========================================
# ML MODEL EXPLANATION
# ==========================================

def generate_explanation(prediction, confidence, top_features):

    prompt = f"""
You are generating a concise model performance summary for a business intelligence dashboard.

Model Status: {prediction}
Confidence Score: {confidence}
Top Features: {top_features}

Write a short, structured summary with the following sections:

MODEL SIGNAL:
- Interpret the confidence level in practical terms (1–2 sentences).

DRIVERS:
- Briefly explain why the top features matter (bullet-style, short).

IMPLICATION:
- State what this means for business monitoring or decision support (1–2 sentences).

RECOMMENDED NEXT STEP:
- One clear, practical improvement action.

Constraints:
- No greetings.
- No email tone.
- No storytelling.
- No placeholders like [Executive].
- No unnecessary explanations.
- Keep it under 180 words.
- Professional, neutral, dashboard-ready tone.
"""

    llm = get_llm()

    response = llm.generate(prompt)

    if not response or "unavailable" in response.lower():
        return fallback_explanation(prediction, confidence, top_features)

    return response


# ==========================================
# GENERIC LLM RESPONSE (RAG Engine)
# ==========================================

def generate_llm_response(prompt: str):

    llm = get_llm()

    response = llm.generate(prompt)

    if not response or "unavailable" in response.lower():
        return fallback_rag_response(prompt)

    return response