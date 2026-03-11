import os
from google import genai
from app.llm.base import BaseLLM


class GeminiProvider(BaseLLM):

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("[LLM] Gemini initialized")
            except Exception as e:
                print("[LLM] Gemini init failed:", e)
        else:
            print("[LLM] GEMINI_API_KEY not found")

    def generate(self, prompt: str) -> str:

        if not self.client:
            return "LLM service unavailable."

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if hasattr(response, "text") and response.text:
                return response.text.strip()

            if hasattr(response, "candidates"):
                return response.candidates[0].content.parts[0].text.strip()

        except Exception as e:
            print("[LLM ERROR]:", str(e))

        return "LLM response unavailable."