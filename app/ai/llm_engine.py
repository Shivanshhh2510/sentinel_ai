import os
from google import genai


# ==========================================
# GEMINI CLIENT INITIALIZATION
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("[OK] Gemini client initialized")
    except Exception:
        client = None
        print("[WARN] Gemini initialization failed — fallback mode")
else:
    print("[WARN] GEMINI_API_KEY not found — running in fallback mode")


# ==========================================
# FALLBACK ML EXPLANATION
# ==========================================

def fallback_explanation(prediction, confidence, top_features):
    """
    Rule-based ML explanation (always works even if Gemini fails)
    """

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
    """
    Fallback if Gemini fails for RAG queries.
    """

    return (
        "Based on the retrieved dataset context, the answer can be derived "
        "from the information shown above. However, AI reasoning service "
        "is currently unavailable."
    )


# ==========================================
# ML MODEL EXPLANATION (AutoML pipeline)
# ==========================================

def generate_explanation(prediction, confidence, top_features):
    """
    Generates explanation for ML predictions.
    Uses Gemini if available, otherwise fallback.
    """

    prompt = f"""
You are an AI assistant explaining a machine learning prediction.

Prediction: {prediction}
Confidence: {confidence}
Top Influencing Factors: {top_features}

Explain in simple, business-friendly language why this prediction happened.
Keep it short, clear, and actionable.
"""

    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if response and hasattr(response, "text") and response.text:
                return response.text.strip()

        except Exception:
            pass

    return fallback_explanation(prediction, confidence, top_features)


# ==========================================
# GENERIC LLM RESPONSE (Used by RAG engine)
# ==========================================

def generate_llm_response(prompt: str):

    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            # DEBUG PRINT
            print("[Gemini answer]:", response)

            # Method 1 (most common)
            if hasattr(response, "text") and response.text:
                return response.text.strip()

            # Method 2 (fallback parsing)
            if hasattr(response, "candidates"):
                return response.candidates[0].content.parts[0].text.strip()

        except Exception as e:
            print("[Gemini ERROR]:", str(e))

    return fallback_rag_response(prompt)