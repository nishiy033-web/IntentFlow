from providers.gemini_provider import GeminiProvider

gemini = GeminiProvider()

response = gemini.generate(
    "Explain what an AI model is in 2 simple sentences."
)

if response:
    print("\nGemini Provider Working!")
    print(response)
else:
    print("\nGemini Provider Failed!")