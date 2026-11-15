
from ai_engine import generate_routed_response


def summarize_conversation(existing_summary, older_messages):

    prompt = f"""
    You are the conversation memory manager of IntentFlow.

    Your task is to create a concise summary of a conversation.

    Previous summary:
    {existing_summary if existing_summary else "No previous summary."}

    New conversation messages:
    {older_messages}

    Instructions:
    1. Preserve important facts and context.
    2. Remember the user's goals, preferences, and decisions.
    3. Preserve unfinished tasks and important technical details.
    4. Remove repeated or irrelevant information.
    5. Do not invent information.
    6. Write the summary in clear, concise language.
    7. Return only the updated summary.
    """

    summary = generate_routed_response(
        prompt,
        intent="general"
    )

    if not summary or not summary.strip():
        return None

    return summary.strip()
