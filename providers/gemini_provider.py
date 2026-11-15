import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from .base_provider import BaseProvider


class GeminiProvider(BaseProvider):

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Gemini API key not found!")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt, json_mode=False):

        try:
            config = types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=20000),
                response_mime_type=(
                    "application/json" if json_mode else "text/plain"
                )
            )

            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=config
            )

            return response.text

        except Exception as e:
            print(f"\nGemini request failed: {type(e).__name__}: {e}")
            return None