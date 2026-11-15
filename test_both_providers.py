
from ai_engine import generate_ai_response, generate_groq_response

prompt = "Explain what an API is in two simple sentences."

print("\n========== GEMINI ==========")

gemini_response = generate_ai_response(prompt)

if gemini_response:
    print("Gemini Working!")
    print(gemini_response)
else:
    print("Gemini Failed!")

print("\n========== GROQ ==========")

groq_response = generate_groq_response(prompt)

if groq_response:
    print("Groq Working!")
    print(groq_response)
else:
    print("Groq Failed!")
