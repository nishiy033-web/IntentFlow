
from agents.research_agent import run_research_agent


def research_assistant(user_request, conversation_history=""):

    return run_research_agent(
        task=user_request,
        conversation_history=conversation_history
    )
