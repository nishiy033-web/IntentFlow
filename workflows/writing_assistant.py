
from ai_engine import generate_routed_response


def writing_assistant(user_request, conversation_history=""):

    prompt = f"""
    You are IntentFlow's professional writing assistant.

    Help the user with their writing request.

    Previous conversation:
    {conversation_history if conversation_history else "No previous conversation."}

    Current user request:
    {user_request}

    Instructions:
    1. Understand the purpose and audience.
    2. Use an appropriate tone.
    3. Keep the writing clear and natural.
    4. Avoid unnecessary complicated language.
    5. Provide the complete requested draft.
    """

    return generate_routed_response(
    prompt=prompt,
    intent="writing"
)
