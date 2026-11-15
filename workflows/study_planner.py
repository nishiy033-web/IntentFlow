
from ai_engine import generate_routed_response


def study_planner(intent_data, conversation_history=""):

    subject = intent_data.get("subject") or "Not specified"
    duration = intent_data.get("duration") or "Not specified"
    task = intent_data.get("task") or "Create a study plan"

    prompt = f"""
    You are an expert academic study planner.

    Create a practical and structured study plan.
    Previous conversation:
    {conversation_history if conversation_history else "No previous conversation."}

    Subject: {subject}
    Available time: {duration}
    Task: {task}

    Include:
    1. Daily topics
    2. Important concepts to cover
    3. Practice questions
    4. Revision sessions
    5. A final preparation checklist

    Keep the plan realistic and student-friendly.
    """

    return generate_routed_response(
    prompt=prompt,
    intent="study_planning"
)