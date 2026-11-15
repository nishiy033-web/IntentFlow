
from agents.coding_agent import run_coding_agent


def coding_assistant(intent_data, user_request, conversation_history=""):

    subject = intent_data.get("subject")

    return run_coding_agent(
    task=user_request,
    subject=subject,
    conversation_history=conversation_history
)
