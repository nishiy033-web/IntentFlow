
from providers.groq_provider import GroqProvider

groq = GroqProvider()

response = groq.generate(
    "Explain recursion in Python using a simple example. Keep it beginner-friendly."
)

if response:
    print("\nGroq Provider Working!")
    print(response)
else:
    print("\nGroq Provider Failed!")
