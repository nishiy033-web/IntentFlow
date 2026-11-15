
def select_model(intent):
    """
    Select the most suitable AI provider
    based on the detected task category.
    """

    if intent == "coding_help":
        return "groq"

    elif intent in [
        "study_planning",
        "complex_reasoning"
    ]:
         return "openai"

    elif intent in [
        "research",
        "writing",
        "general"
    ]:
        return "gemini"

    else:
        return "gemini"
