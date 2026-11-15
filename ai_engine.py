
import json
from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider
from model_selector import select_model
from providers.openai_provider import OpenAIProvider


# Initialize AI providers
gemini = GeminiProvider()
groq = GroqProvider()
openai_provider = OpenAIProvider()


# Gemini response function (existing workflows)
def generate_ai_response(prompt, json_mode=False):
    return gemini.generate(
        prompt=prompt,
        json_mode=json_mode
    )


# Groq response function
def generate_groq_response(prompt, json_mode=False):
    return groq.generate(
        prompt=prompt,
        json_mode=json_mode
    )
# OpenAI response function
def generate_openai_response(prompt, json_mode=False):
    return openai_provider.generate(
        prompt=prompt,
        json_mode=json_mode
    )


def generate_routed_response(prompt, intent, json_mode=False):

    selected_model = select_model(intent)

    print(f"\nIntentFlow selected: {selected_model.upper()}")

    providers = {
        "gemini": generate_ai_response,
        "groq": generate_groq_response,
        "openai": generate_openai_response
    }

    # Try the selected provider first, then the alternatives.
    fallback_order = [selected_model] + [
        provider for provider in ["gemini", "groq", "openai"]
        if provider != selected_model
    ]

    for provider_name in fallback_order:

        print(f"\nTrying {provider_name.upper()}...")

        response = providers[provider_name](
            prompt=prompt,
            json_mode=json_mode
        )

        if response:
            print(f"\nResponse generated successfully: {provider_name.upper()}")
            return response

        print(f"\n{provider_name.upper()} failed.")

    return (
        "Sorry, all AI providers are currently unavailable. "
        "Please try again later."
    )

def generate_intent_response(prompt):

    # Try Gemini first
    providers = [
        ("Gemini", generate_ai_response),
        ("Groq", generate_groq_response)
    ]

    for provider_name, provider_function in providers:

        print(f"\nIntent detection trying: {provider_name}")

        response = provider_function(
            prompt=prompt,
            json_mode=True
        )

        if not response:
            continue

        try:
            intent_data = json.loads(response)

            if isinstance(intent_data, dict):
                print(f"Intent detection successful: {provider_name}")
                return intent_data

        except (json.JSONDecodeError, TypeError):
            print(f"{provider_name} returned invalid JSON.")

    print("\nAll intent detection providers failed.")

    return None


def is_semantic_duplicate_memory(new_memory, existing_memories):

    if not existing_memories:
        return False

    memories_text = "\n".join(
        f"- {memory}" for memory in existing_memories
    )

    prompt = f"""
You are IntentFlow's Memory Duplicate Detector.

Compare the NEW MEMORY with the EXISTING MEMORIES.

Determine whether the new memory expresses the same
underlying fact, goal, preference, decision, or information
as any existing memory.

Rules:
- Different wording with the same meaning = duplicate.
- Same broad topic but different information = NOT duplicate.
- Related but distinct goals = NOT duplicate.
- Be careful not to mark unrelated memories as duplicates.

NEW MEMORY:
{new_memory}

EXISTING MEMORIES:
{memories_text}

Return ONLY valid JSON:

{{
    "is_duplicate": true
}}

Use false if no existing memory has the same underlying meaning.
"""

    response = generate_routed_response(
        prompt=prompt,
        intent="general",
        json_mode=True
    )

    if not response:
        return False

    try:
        data = json.loads(response)

        return data.get("is_duplicate", False) is True

    except (json.JSONDecodeError, AttributeError, TypeError):
        return False



def extract_explicit_memory_content(conversation_text, user_request):

    prompt = f"""
You are IntentFlow's Personal Memory Assistant.

The user has explicitly asked to save a goal, preference,
project or other information to Global Personal Memory.

Your task is to identify the ACTUAL information they want
to save from the conversation.

IMPORTANT RULES:
- Use the conversation history to identify the actual information.
- The latest user request tells you what they want saved.
- Do NOT save the command itself.
- Do NOT save sentences like "Remember this" or
  "Save my goal" as memories.
- Prefer the user's original meaning and wording.
- Do not invent or assume missing information.
- If the intended information cannot be identified,
  return an empty memory.
- Choose the most appropriate category.

Return ONLY valid JSON in this exact format:

{{
    "memory": "The actual information to remember",
    "category": "goal"
}}

Allowed categories:
general, goal, preference, learning, project, personal

If the information cannot be identified, return:

{{
    "memory": "",
    "category": "general"
}}

CONVERSATION HISTORY:
{conversation_text}

LATEST USER REQUEST:
{user_request}
"""

    response = generate_routed_response(
        prompt=prompt,
        intent="general",
        json_mode=True
    )

    if not response:
        return None

    try:
        data = json.loads(response)

        if not isinstance(data, dict):
            return None

        memory = data.get("memory", "").strip()
        category = data.get("category", "general").lower()

        valid_categories = {
            "general",
            "goal",
            "preference",
            "learning",
            "project",
            "personal"
        }

        if not memory:
            return None

        if category not in valid_categories:
            category = "general"

        return {
            "memory": memory,
            "category": category
        }

    except (json.JSONDecodeError, AttributeError, TypeError):
        return None

