
from intent_detector import detect_intent
from workflows.study_planner import study_planner
from workflows.coding_assistant import coding_assistant
from workflows.writing_assistant import writing_assistant
from workflows.general_assistant import general_assistant
from workflows.research_assistant import research_assistant
# -------------------------------
# MAIN APPLICATION
# -------------------------------


def main():

    user_request = input(
        "\nWelcome to IntentFlow!\n"
        "What would you like IntentFlow to do? "
    ).strip()

    if not user_request:
        print("Please enter a valid request.")
        return

    # Detect user intent
    intent_data = detect_intent(user_request)

    if intent_data is None:
        print("\nCould not detect your intent. Please try again.")
        return

    print("\nDetected intent:")
    print(intent_data)

    intent = intent_data["intent"]

    # Route request to the appropriate workflow
    print("\nLaunching your assistant...")

    if intent == "study_planning":
        print("\nLaunching Study Planner...")
        result = study_planner(intent_data)

    elif intent == "coding_help":
        print("\nLaunching Coding Assistant...")
        result = coding_assistant(intent_data, user_request)

    elif intent == "writing":
        print("\nLaunching Writing Assistant...")
        result = writing_assistant(user_request)

    elif intent == "research":
        print("\nLaunching Research Assistant...")
        result = research_assistant(user_request)

    else:
        print("\nLaunching General Assistant...")
        result = general_assistant(user_request)

    # Display response safely
    if result:
        print("\n" + result)
    else:
        print("\nSorry, IntentFlow couldn't generate a response.")
        print("Please try again later.")


if __name__ == "__main__":
    main()

