
from ai_engine import generate_routed_response


def general_assistant(user_request, conversation_history=""):

    prompt = f"""
    You are IntentFlow's helpful general-purpose AI assistant.

    Answer the user's question clearly and accurately.

    Previous conversation:
    {conversation_history if conversation_history else "No previous conversation."}

    Current user request:
    {user_request}

    Instructions:
    1. Explain concepts in simple language.
    2. Give examples wherever useful.
    3. Keep answers relevant to the question.
    4. Avoid unnecessary complicated language.
    """

    return generate_routed_response(
    prompt=prompt,
    intent="general"
)
