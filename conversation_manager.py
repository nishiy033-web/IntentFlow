
from database import (
    get_messages,
    get_conversation_summary,
    get_summary_checkpoint,
    save_conversation_summary
)

from summarization import summarize_conversation


def get_conversation_history(conversation_id, limit=10):
    """
    Retrieve conversation summary and recent messages.
    """

    if conversation_id is None:
        return ""

    if limit <= 0:
        return ""

    # Retrieve existing summary
    summary = get_conversation_summary(conversation_id)

    # Retrieve all messages
    messages = get_messages(conversation_id)

    # Keep the most recent messages
    recent_messages = messages[-limit:]

    history = []

    # Add summary first
    if summary:

        history.append(
            f"Previous Conversation Summary:\n{summary}"
        )

    # Add recent messages
    recent_history = []

    for message in recent_messages:

        role = message[1]
        content = message[2]

        if role == "user":
            speaker = "User"

        elif role == "assistant":
            speaker = "IntentFlow"

        else:
            continue

        recent_history.append(f"{speaker}: {content}")

    if recent_history:

        history.append(
            "Recent Conversation:\n" + "\n".join(recent_history)
        )

    return "\n\n".join(history)
def update_conversation_summary(conversation_id, recent_limit=10):
    """
    Update the conversation summary using older messages
    while keeping the most recent messages untouched.
    """

    if conversation_id is None or recent_limit <= 0:
        return False

    # Retrieve all messages
    messages = get_messages(conversation_id)

    # Don't summarize if there aren't enough messages
    if len(messages) <= recent_limit:
        return False

    # Separate older messages from recent messages
    older_messages = messages[:-recent_limit]

    # Get the previous summary checkpoint
    last_message_id = get_summary_checkpoint(conversation_id)

    # Select only messages that haven't been summarized yet
    if last_message_id is None:

        new_messages = older_messages

    else:

        new_messages = [
            message for message in older_messages
            if message[0] > last_message_id
        ]

    # Nothing new to summarize
    if not new_messages:
        return False

    # Retrieve existing summary
    existing_summary = get_conversation_summary(conversation_id)

    # Format messages for the summarization model
    formatted_messages = []

    for message in new_messages:

        role = message[1]
        content = message[2]

        if role == "user":
            speaker = "User"

        elif role == "assistant":
            speaker = "IntentFlow"

        else:
            continue

        formatted_messages.append(f"{speaker}: {content}")

    if not formatted_messages:
        return False

    conversation_text = "\n".join(formatted_messages)

    # Generate updated summary
    updated_summary = summarize_conversation(
        existing_summary,
        conversation_text
    )

    if not updated_summary:
        return False

    # Save updated summary and checkpoint
    new_checkpoint = new_messages[-1][0]

    save_conversation_summary(
        conversation_id,
        updated_summary,
        new_checkpoint
    )

    return True
