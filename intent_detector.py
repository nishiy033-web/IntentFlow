
from ai_engine import generate_intent_response


def detect_intent(user_request, conversation_history=""):
    prompt = f"""
    You are the intent detection engine of IntentFlow.

    Analyze the user's request and classify it into exactly one of:

    - study_planning
    - coding_help
    - writing
    - research
    - general

    Classification guidelines:

    - study_planning: Creating study plans, exam preparation,
      revision schedules and learning plans.
    - coding_help: Programming, debugging, DSA and technical coding questions.
    - writing: Emails, articles, reports and other writing tasks.
    - research: Web research, latest developments, current information,
      fact-finding and requests requiring external sources.
    - general: Casual conversation, greetings and general questions
      that do not require a specialised workflow.

    Return valid JSON with these four keys:
    - intent
    - task
    - subject
    - duration

    Use null when a field is not relevant.

   Previous conversation:
   {conversation_history if conversation_history else "No previous conversation."}

   Current user request:
   {user_request}
    """

    intent_data = generate_intent_response(prompt)

    if not intent_data:
        return None

    valid_intents = [
        "study_planning",
        "coding_help",
        "writing",
        "research",
        "general"
    ]

    if intent_data.get("intent") not in valid_intents:
        return None

    return intent_data
