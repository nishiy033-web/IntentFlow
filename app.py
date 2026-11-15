
import streamlit as st

from database import (
    initialize_database,
    create_conversation,
    get_all_conversations,
    save_message,
    get_messages,
    rename_conversation,
    delete_conversation,
    search_messages,
    create_group,
    get_all_groups,
    move_conversation,
    rename_group,
    delete_group,
    save_global_memory,
    get_all_global_memories,
    update_global_memory,
    delete_global_memory,
)

from intent_detector import detect_intent
from ai_engine import (
    extract_explicit_memory_content,
    is_semantic_duplicate_memory
)
from workflows.study_planner import study_planner
from workflows.coding_assistant import coding_assistant
from workflows.writing_assistant import writing_assistant
from workflows.general_assistant import general_assistant
from workflows.research_assistant import research_assistant
from conversation_manager import (
    get_conversation_history,
    update_conversation_summary
)
from memory_manager import (
    get_global_memory_context,
    is_explicit_memory_request
)


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="IntentFlow",
    page_icon="⚡",
    layout="centered"
)
st.markdown("""
<style>
div[id^="message-"]:target {
    display: block;
    height: 10px;
    background-color: #f5c542;
    border-radius: 8px;
    outline: 3px solid rgba(245, 197, 66, 0.35);
    margin-bottom: 8px;
    scroll-margin-top: 100px;
}
</style>
""", unsafe_allow_html=True)

initialize_database()



def save_message_to_personal_memory(message_content, conversation_id):

    # Extract meaningful information from the selected message
    memory_data = extract_explicit_memory_content(
        conversation_text=f"USER MESSAGE:\n{message_content}",
        user_request="Please save the information in this message to Personal Memory."
    )

    if not memory_data:
        return False, "I couldn't identify useful information to remember."

    new_memory = memory_data["memory"]
    category = memory_data["category"]

    # Collect existing saved memories
    existing_memories = get_all_global_memories()

    existing_texts = [
        memory[1] for memory in existing_memories
    ]

    # Check exact duplicates
    normalized_new = " ".join(new_memory.lower().split())

    for existing in existing_texts:

        normalized_existing = " ".join(
            existing.lower().split()
        )

        if normalized_new == normalized_existing:
            return False, "This memory is already saved in Personal Memory."

    # Check semantic duplicates
    if is_semantic_duplicate_memory(
        new_memory,
        existing_texts
    ):
        return False, "A similar memory already exists in Personal Memory."

    # Save directly to Global Personal Memory
    save_global_memory(
        new_memory,
        category,
        conversation_id
    )

    return True, "Successfully saved to Personal Memory!"




# ---------------- SESSION STATE ----------------

if "active_conversation_id" not in st.session_state:
    st.session_state.active_conversation_id = None

if "expanded_collections" not in st.session_state:
    st.session_state.expanded_collections = set()

if "selected_collection_id" not in st.session_state:
    st.session_state.selected_collection_id = None

def render_chat_item(chat, collections, location):

    chat_id = chat[0]
    chat_title = chat[1]
    group_id = chat[2]

    chat_col, menu_col = st.columns([0.85, 0.15])

    # Chat button
    with chat_col:
        if st.button(
            f"💬 {chat_title}",
            key=f"{location}_chat_{chat_id}",
            use_container_width=True
        ):
            st.session_state.active_conversation_id = chat_id
            st.session_state.selected_collection_id = group_id
            st.rerun()

    # Three-dot menu toggle
    with menu_col:
        if st.button(
            "⋮",
            key=f"menu_toggle_{chat_id}",
            use_container_width=True
        ):
            if st.session_state.get("open_chat_menu_id") == chat_id:
                st.session_state.open_chat_menu_id = None
            else:
                st.session_state.open_chat_menu_id = chat_id

            st.rerun()

    # Show menu when this chat is selected
    if st.session_state.get("open_chat_menu_id") == chat_id:

        with st.container(border=True):

            st.markdown("**Chat Actions**")

            # Rename
            new_title = st.text_input(
                "Chat name",
                value=chat_title,
                key=f"rename_input_{chat_id}"
            )

            if st.button("Rename", key=f"rename_btn_{chat_id}"):
                if new_title.strip():
                    rename_conversation(chat_id, new_title.strip())
                    st.session_state.open_chat_menu_id = None
                    st.rerun()

            st.divider()

            # Move to Collection
            collection_ids = [None] + [c[0] for c in collections]

            current_index = (
                collection_ids.index(group_id)
                if group_id in collection_ids
                else 0
            )

            selected_group = st.selectbox(
                "Move to",
                options=collection_ids,
                index=current_index,
                format_func=lambda gid: (
                    "Recent Chats"
                    if gid is None
                    else next(c[1] for c in collections if c[0] == gid)
                ),
                key=f"move_select_{chat_id}"
            )

            if st.button("Move Chat", key=f"move_btn_{chat_id}"):

                move_conversation(chat_id, selected_group)

                st.session_state.selected_collection_id = selected_group
                st.session_state.open_chat_menu_id = None

                if selected_group is not None:
                    st.session_state.expanded_collections.add(selected_group)

                st.rerun()

            st.divider()

            # Delete Chat
            confirm_delete = st.checkbox(
                "Confirm deletion",
                key=f"confirm_delete_{chat_id}"
            )

            if st.button(
                "Delete Chat",
                key=f"delete_btn_{chat_id}",
                disabled=not confirm_delete
            ):

                delete_conversation(chat_id)

                if st.session_state.active_conversation_id == chat_id:
                    st.session_state.active_conversation_id = None

                st.session_state.open_chat_menu_id = None
                st.rerun()
        


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("💬 Chat Library")

    collections = get_all_groups()
    conversations = get_all_conversations()

    valid_collection_ids = [c[0] for c in collections]

    # Reset selected collection if it was deleted
    if st.session_state.selected_collection_id not in valid_collection_ids:
        st.session_state.selected_collection_id = None

    # ---------------- NEW CHAT ----------------

    if st.button("➕ New Chat", use_container_width=True):

        new_id = create_conversation(
            group_id=st.session_state.selected_collection_id
        )

        st.session_state.active_conversation_id = new_id
        st.rerun()

    st.divider()

    # ---------------- COLLECTIONS ----------------

    st.subheader("📁 Collections")

    with st.expander("➕ Create Collection"):

        collection_name = st.text_input(
            "Collection name",
            key="new_collection_name"
        )

        if st.button("Create", key="create_collection"):

            if collection_name.strip():

                create_group(collection_name.strip())
                st.rerun()

            else:
                st.warning("Enter a collection name.")

    # Display collections
    for collection in collections:

        collection_id = collection[0]
        collection_title = collection[1]

        is_expanded = (
            collection_id in st.session_state.expanded_collections
        )

        arrow = "▼" if is_expanded else "▶"

        if st.button(
            f"{arrow} 📁 {collection_title}",
            key=f"collection_{collection_id}",
            use_container_width=True
        ):

            expanded = set(st.session_state.expanded_collections)

            if collection_id in expanded:
                expanded.remove(collection_id)
            else:
                expanded.add(collection_id)

            st.session_state.expanded_collections = expanded
            st.session_state.selected_collection_id = collection_id

            st.rerun()

        # Display chats inside expanded collection
        if is_expanded:
            collection_chats = [
                chat for chat in conversations
                if chat[2] == collection_id
            ]

            for chat in collection_chats:
                render_chat_item(
                    chat,
                    collections,
                    f"collection_{collection_id}"
                )

            if not collection_chats:
                st.caption("　No chats in this collection yet.")

            # Collection settings
            with st.expander("⚙️ Collection Settings"):

                new_name = st.text_input(
                    "Rename collection",
                    value=collection_title,
                    key=f"rename_collection_{collection_id}"
                )

                if st.button(
                    "✏️ Rename",
                    key=f"rename_group_{collection_id}"
                ):

                    if new_name.strip():

                        rename_group(collection_id, new_name.strip())
                        st.rerun()

                    else:
                        st.warning("Name cannot be empty.")

                confirm_delete = st.checkbox(
                    "Confirm deletion",
                    key=f"confirm_delete_group_{collection_id}"
                )

                if st.button(
                    "🗑️ Delete Collection",
                    key=f"delete_group_{collection_id}",
                    disabled=not confirm_delete
                ):

                    delete_group(collection_id)

                    st.session_state.selected_collection_id = None
                    st.session_state.expanded_collections.discard(collection_id)

                    st.rerun()

    st.divider()

    # ---------------- PERSONAL MEMORY ----------------

    st.subheader("🧠 Personal Memory")

    memories = get_all_global_memories()

    st.caption(f"{len(memories)} saved memories")

    # Add new memory
    with st.expander("➕ Add Memory"):

        new_memory_text = st.text_area(
            "What should IntentFlow remember?",
            key="new_memory_text"
        )

        new_memory_category = st.selectbox(
            "Category",
            [
                "general",
                "goal",
                "preference",
                "learning",
                "project",
                "personal"
            ],
            key="new_memory_category"
        )

        if st.button(
            "💾 Save Memory",
            key="save_global_memory",
            use_container_width=True
        ):

            if new_memory_text.strip():

                save_global_memory(
                    new_memory_text.strip(),
                    new_memory_category
                )

                st.success("Memory saved!")
                st.rerun()

            else:
                st.warning("Please enter a memory.")

    # Display saved memories
    if memories:

        for memory in memories:

            memory_id = memory[0]
            memory_text = memory[1]
            memory_category = memory[2]

            with st.expander(
                f"📝 {memory_category.title()} — {memory_text[:45]}"
            ):

                st.write(memory_text)

                st.caption(f"Memory ID: {memory_id}")

                # Edit memory
                edited_memory = st.text_area(
                    "Edit memory",
                    value=memory_text,
                    key=f"edit_memory_{memory_id}"
                )

                edited_category = st.selectbox(
                    "Category",
                    [
                        "general",
                        "goal",
                        "preference",
                        "learning",
                        "project",
                        "personal"
                    ],
                    index=[
                        "general",
                        "goal",
                        "preference",
                        "learning",
                        "project",
                        "personal"
                    ].index(memory_category)
                    if memory_category in [
                        "general",
                        "goal",
                        "preference",
                        "learning",
                        "project",
                        "personal"
                    ] else 0,
                    key=f"edit_category_{memory_id}"
                )

                if st.button(
                    "✏️ Update Memory",
                    key=f"update_memory_{memory_id}",
                    use_container_width=True
                ):

                    if edited_memory.strip():

                        update_global_memory(
                            memory_id,
                            edited_memory.strip(),
                            edited_category
                        )

                        st.success("Memory updated!")
                        st.rerun()

                    else:
                        st.warning("Memory cannot be empty.")

                if st.button(
                    "🗑️ Delete Memory",
                    key=f"delete_memory_{memory_id}",
                    use_container_width=True
                ):

                    delete_global_memory(memory_id)

                    st.success("Memory deleted!")
                    st.rerun()

    else:

        st.caption("No saved memories yet.")


    # ---------------- RECENT CHATS ----------------

    st.subheader("Recent Chats")

    recent_chats = [
        chat for chat in conversations
        if chat[2] is None
    ]

    for chat in recent_chats:
        render_chat_item(
            chat,
            collections,
            "recent"
    )


# ---------------- MAIN SCREEN ----------------

st.title("⚡ IntentFlow")

st.subheader("Your Intelligent AI Request Orchestrator")

st.write(
    "Tell IntentFlow what you need. "
    "It will understand your request and connect you "
    "to the right AI assistant."
)

st.divider()

# ---------------- ACTIVE CONVERSATION ----------------

active_id = st.session_state.active_conversation_id

if active_id is None:

    st.info("Start a new chat or select a conversation from the sidebar.")

else:

    conversations = get_all_conversations()

    current_conversation = next(
        (chat for chat in conversations if chat[0] == active_id),
        None
    )

    # Handle deleted or unavailable conversation
    if current_conversation is None:

        st.session_state.active_conversation_id = None
        st.rerun()

    else:

        current_title = current_conversation[1]
        current_group_id = current_conversation[2]

        # ---------------- CHAT LAYOUT ----------------

        conversation_col, search_col = st.columns([3, 1])

        # ---------------- CONVERSATION HISTORY ----------------

        with conversation_col:

            st.markdown("### 💬 Conversation")

            messages = get_messages(active_id)

            for message in messages:

                message_id = message[0]
                role = message[1]
                content = message[2]

                st.markdown(
                    f'<div id="message-{message_id}"></div>',
                    unsafe_allow_html=True
                )


                with st.chat_message(role):
                    st.markdown(content)

                    if role == "user":

                        if st.button(
                            "🔖 Save to Personal Memory",
                            key=f"save_memory_{message_id}"
                        ):

                            with st.spinner("Preparing your memory..."):

                                success, message = save_message_to_personal_memory(
                                    content,
                                    active_id
                                )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.info(message)


        # ---------------- SEARCH IN CHAT ----------------

        with search_col:

            st.markdown("### 🔍 Search")

            search_query = st.text_input(
                "Find a word or phrase",
                key=f"search_{active_id}",
                placeholder="Search messages..."
            )

            search_mode = st.radio(
                "Search mode",
                ["All Messages", "My Questions"],
                key=f"search_mode_{active_id}"
            )

            if search_query.strip():

                results = search_messages(
                    active_id,
                    search_query.strip(),
                    user_only=(search_mode == "My Questions")
                )

                st.caption(
                    f"{len(results)} matching messages found"
                )

                if results:

                    for result in results:

                        message_id, role, content, created_at = result

                        with st.container(border=True):

                            st.caption(
                                f"{'You' if role == 'user' else 'IntentFlow'} "
                                f"· Message #{message_id}"
                            )

                            st.markdown(content)

                            st.markdown(
                                f'<a href="#message-{message_id}">'
                                f'↗ Jump to original message</a>',
                                unsafe_allow_html=True
                            )                        


# ---------------- USER INPUT ----------------

with st.form("intentflow_form", clear_on_submit=True):

    user_request = st.text_area(
        "What would you like IntentFlow to do?",
        placeholder="Example: Create a 7-day Python study plan...",
        height=100
    )

    submit_button = st.form_submit_button(
        "Run IntentFlow 🚀",
        use_container_width=True
    )



# ---------------- PROCESS REQUEST ----------------

if submit_button:

    if not user_request.strip():

        st.warning("Please enter a request first.")

    else:

        # Create conversation if none is selected
        if st.session_state.active_conversation_id is None:

            new_id = create_conversation(
                group_id=st.session_state.selected_collection_id
            )

            st.session_state.active_conversation_id = new_id

        active_id = st.session_state.active_conversation_id

        # Detect explicit memory-saving request
        explicit_memory = is_explicit_memory_request(user_request)

        # Get current conversation history and global memory
        conversation_history = get_conversation_history(active_id)
        global_memory_context = get_global_memory_context()

        # Combine both contexts
        assistant_context = f"""
GLOBAL PERSONAL MEMORY:
{global_memory_context if global_memory_context else "No saved global memories."}

CURRENT CONVERSATION HISTORY:
{conversation_history if conversation_history else "No previous conversation."}
"""

        # Save user message
        save_message(
            active_id,
            "user",
            user_request
        )

        # Generate automatic title for first message
        existing_messages = get_messages(active_id)

        if len(existing_messages) == 1:

            title = user_request.strip().replace("\n", " ")

            if len(title) > 35:
                title = title[:35] + "..."

            rename_conversation(active_id, title)





        # Handle explicit memory requests
        if explicit_memory:

            memory_data = extract_explicit_memory_content(
                conversation_history,
                user_request
            )

            if memory_data:

                new_memory = memory_data["memory"]
                category = memory_data["category"]

                # Check existing saved memories
                existing_memories = get_all_global_memories()

                existing_texts = [
                    memory[1] for memory in existing_memories
                ]

                normalized_new = " ".join(
                    new_memory.lower().split()
                )

                exact_duplicate = any(
                    normalized_new == " ".join(
                        existing.lower().split()
                    )
                    for existing in existing_texts
                )

                if exact_duplicate:

                    result = (
                        "ℹ️ This information is already saved "
                        "in your Personal Memory."
                    )

                elif is_semantic_duplicate_memory(
                    new_memory,
                    existing_texts
                ):

                    result = (
                        "ℹ️ A similar memory already exists "
                        "in your Personal Memory."
                    )

                else:

                    save_global_memory(
                        new_memory,
                        category,
                        active_id
                    )

                    result = (
                        "❤️ Successfully saved to Personal Memory!\n\n"
                        f"**Memory:** {new_memory}\n\n"
                        f"**Category:** {category.title()}"
                    )

            else:

                result = (
                    "I couldn't confidently identify which goal or "
                    "information you want to save.\n\n"
                    "Please mention the goal again so I can identify it correctly."
                )

            intent_data = None

        else:

            # Detect intent
            with st.spinner("Understanding your request..."):

                intent_data = detect_intent(
                    user_request,
                    conversation_history
                )

            if intent_data is None:

                result = (
                    "I couldn't understand your request. "
                    "Please try again."
                )

            else:

                intent = intent_data["intent"]

                # Route to correct workflow
                with st.spinner("Your AI assistant is working..."):

                    if intent == "study_planning":

                        result = study_planner(
                            intent_data,
                            assistant_context
                        )

                    elif intent == "coding_help":

                        result = coding_assistant(
                            intent_data,
                            user_request,
                            assistant_context
                        )

                    elif intent == "writing":

                        result = writing_assistant(
                            user_request,
                            assistant_context
                        )

                    elif intent == "research":

                        result = research_assistant(
                            user_request,
                            assistant_context
                        )

                    else:

                        result = general_assistant(
                            user_request,
                            assistant_context
                        )



        # Save assistant response
        if not result:

            result = (
                "Sorry, the AI could not generate a response. "
                "Please try again."
            )

        save_message(
            active_id,
            "assistant",
            result,
            intent_data["intent"] if intent_data else None
        )



        # Update conversation memory automatically
        with st.spinner("Updating conversation memory..."):

            update_conversation_summary(active_id)

        st.rerun()



# ---------------- FOOTER ----------------

st.divider()

st.caption("IntentFlow | Powered by Python and Gemini AI")
