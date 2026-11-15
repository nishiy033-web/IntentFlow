
import os
from dotenv import load_dotenv
from openai import OpenAI

from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OpenAI API key not found!")

        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt, json_mode=False):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format=(
                    {"type": "json_object"}
                    if json_mode
                    else {"type": "text"}
                )
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"\nOpenAI request failed: {type(e).__name__}: {e}")
            return None
