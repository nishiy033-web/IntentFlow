
import os
from dotenv import load_dotenv
from groq import Groq

from .base_provider import BaseProvider


class GroqProvider(BaseProvider):

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("Groq API key not found!")

        self.client = Groq(api_key=api_key)

    def generate(self, prompt, json_mode=False):
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format=(
                    {"type": "json_object"} if json_mode else {"type": "text"}
                )
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"\nGroq request failed: {type(e).__name__}: {e}")
            return None
