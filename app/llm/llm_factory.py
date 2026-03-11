from app.llm.gemini_provider import GeminiProvider


def get_llm():
    """
    Central LLM access point.
    Future: can switch to OpenAI/Claude easily.
    """
    return GeminiProvider()