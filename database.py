
import sqlite3
import os


# Database file location
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "intentflow.db"
)


# Connect to database
def get_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# Create database tables
def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # Table 1: Chat Groups
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_groups (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # Table 2: Conversations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL DEFAULT 'New Chat',

            group_id INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (group_id)
                REFERENCES chat_groups(id)
                ON DELETE SET NULL

        )
    """)

    # Table 3: Messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id INTEGER NOT NULL,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            intent TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE

        )
    """)

    # Table 4: Conversation Summaries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_summaries (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id INTEGER NOT NULL UNIQUE,

            summary TEXT NOT NULL,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE

        )
    """)
        # Add checkpoint column if it doesn't exist
    cursor.execute("PRAGMA table_info(conversation_summaries)")

    columns = [column[1] for column in cursor.fetchall()]

    if "last_message_id" not in columns:

        cursor.execute("""
            ALTER TABLE conversation_summaries
            ADD COLUMN last_message_id INTEGER
        """)
    
    # Table 5: Global Personal Memory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_memory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            memory TEXT NOT NULL,

            category TEXT NOT NULL DEFAULT 'general',

            source_conversation_id INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (source_conversation_id)
                REFERENCES conversations(id)
                ON DELETE SET NULL

        )
    """)

    # Table 6: Memory Suggestions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_suggestions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            memory TEXT NOT NULL,

            normalized_memory TEXT NOT NULL UNIQUE,

            category TEXT NOT NULL DEFAULT 'general',

            source_conversation_id INTEGER,

            status TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN ('pending', 'saved', 'dismissed')),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (source_conversation_id)
                REFERENCES conversations(id)
                ON DELETE SET NULL

        )
    """)




    connection.commit()

    connection.close()

# Create a new conversation
def create_conversation(title="New Chat", group_id=None):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (title, group_id)
        VALUES (?, ?)
        """,
        (title, group_id)
    )

    conversation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return conversation_id


# Save a message in a conversation
def save_message(conversation_id, role, content, intent=None):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (conversation_id, role, content, intent)
        VALUES (?, ?, ?, ?)
        """,
        (conversation_id, role, content, intent)
    )

    cursor.execute(
        """
        UPDATE conversations
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (conversation_id,)
    )

    connection.commit()
    connection.close()


# Retrieve all conversations
def get_all_conversations():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title, group_id, created_at, updated_at
        FROM conversations
        ORDER BY updated_at DESC
        """
    )

    conversations = cursor.fetchall()

    connection.close()

    return conversations


# Retrieve messages from a particular conversation
def get_messages(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, role, content, intent, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,)
    )

    messages = cursor.fetchall()

    connection.close()

    return messages


def save_conversation_summary(conversation_id, summary, last_message_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversation_summaries
        (conversation_id, summary, last_message_id)

        VALUES (?, ?, ?)

        ON CONFLICT(conversation_id)
        DO UPDATE SET
            summary = excluded.summary,
            last_message_id = excluded.last_message_id,
            updated_at = CURRENT_TIMESTAMP
        """,
        (conversation_id, summary, last_message_id)
    )

    connection.commit()
    connection.close()


def get_conversation_summary(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT summary
        FROM conversation_summaries
        WHERE conversation_id = ?
        """,
        (conversation_id,)
    )

    result = cursor.fetchone()

    connection.close()

    return result[0] if result else ""
def get_summary_checkpoint(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT last_message_id
        FROM conversation_summaries
        WHERE conversation_id = ?
        """,
        (conversation_id,)
    )

    result = cursor.fetchone()

    connection.close()

    return result[0] if result else None


# Create a new chat group
def create_group(name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO chat_groups (name) VALUES (?)",
        (name,)
    )

    group_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return group_id


# Retrieve all chat groups
def get_all_groups():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, created_at
        FROM chat_groups
        ORDER BY name ASC
        """
    )

    groups = cursor.fetchall()

    connection.close()

    return groups

# Move a conversation into a group or ungroup it
def move_conversation(conversation_id, group_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET group_id = ?
        WHERE id = ?
        """,
        (group_id, conversation_id)
    )

    connection.commit()
    connection.close()


# Rename a conversation
def rename_conversation(conversation_id, new_title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET title = ?
        WHERE id = ?
        """,
        (new_title, conversation_id)
    )

    connection.commit()
    connection.close()

# Delete a conversation and its messages
def delete_conversation(conversation_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM conversations WHERE id = ?",
        (conversation_id,)
    )

    connection.commit()
    connection.close()


# Rename a chat group
def rename_group(group_id, new_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE chat_groups SET name = ? WHERE id = ?",
        (new_name, group_id)
    )

    connection.commit()
    connection.close()



def delete_group(group_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Delete all conversations inside this collection
    cursor.execute(
        "DELETE FROM conversations WHERE group_id = ?",
        (group_id,)
    )

    # Delete the collection itself
    cursor.execute(
        "DELETE FROM chat_groups WHERE id = ?",
        (group_id,)
    )

    conn.commit()
    conn.close()


# Search conversations by title or message content
def search_conversations(search_query):
    connection = get_connection()
    cursor = connection.cursor()

    query = f"%{search_query}%"

    cursor.execute(
        """
        SELECT DISTINCT conversations.id,
                        conversations.title,
                        conversations.group_id,
                        conversations.created_at,
                        conversations.updated_at
        FROM conversations
        LEFT JOIN messages
        ON conversations.id = messages.conversation_id
        WHERE conversations.title LIKE ?
        OR messages.content LIKE ?
        ORDER BY conversations.updated_at DESC
        """,
        (query, query)
    )

    results = cursor.fetchall()
    connection.close()
    return results


# Search messages inside one conversation
def search_messages(conversation_id, search_query, user_only=False):
    connection = get_connection()
    cursor = connection.cursor()

    query = f"%{search_query}%"

    if user_only:
        cursor.execute(
            """
            SELECT id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            AND role = 'user'
            AND content LIKE ?
            ORDER BY id ASC
            """,
            (conversation_id, query)
        )
    else:
        cursor.execute(
            """
            SELECT id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            AND content LIKE ?
            ORDER BY id ASC
            """,
            (conversation_id, query)
        )

    results = cursor.fetchall()
    connection.close()

    return results



if __name__ == "__main__":

    initialize_database()

    print("IntentFlow database initialized successfully!")

# ==========================================
# GLOBAL PERSONAL MEMORY FUNCTIONS
# ==========================================


def save_global_memory(memory, category="general", source_conversation_id=None):

    memory = " ".join(memory.strip().split())

    if not memory:
        raise ValueError("Memory cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    # Check whether the same memory already exists
    cursor.execute("""
        SELECT id
        FROM global_memory
        WHERE LOWER(TRIM(memory)) = LOWER(?)
        LIMIT 1
    """, (memory,))

    existing_memory = cursor.fetchone()

    # Return existing ID instead of creating a duplicate
    if existing_memory:
        connection.close()
        return existing_memory[0]

    # Save new memory
    cursor.execute("""
        INSERT INTO global_memory
        (memory, category, source_conversation_id)
        VALUES (?, ?, ?)
    """, (memory, category, source_conversation_id))

    memory_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return memory_id


def get_all_global_memories(category=None):

    connection = get_connection()
    cursor = connection.cursor()

    if category:
        cursor.execute("""
            SELECT id, memory, category, source_conversation_id,
                   created_at, updated_at
            FROM global_memory
            WHERE category = ?
            ORDER BY updated_at DESC
        """, (category,))
    else:
        cursor.execute("""
            SELECT id, memory, category, source_conversation_id,
                   created_at, updated_at
            FROM global_memory
            ORDER BY updated_at DESC
        """)

    memories = cursor.fetchall()

    connection.close()

    return memories


def update_global_memory(memory_id, new_memory, new_category=None):

    new_memory = new_memory.strip()

    if not new_memory:
        raise ValueError("Memory cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    if new_category:
        cursor.execute("""
            UPDATE global_memory
            SET memory = ?, category = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_memory, new_category, memory_id))
    else:
        cursor.execute("""
            UPDATE global_memory
            SET memory = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_memory, memory_id))

    updated = cursor.rowcount

    connection.commit()
    connection.close()

    return updated > 0


def delete_global_memory(memory_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM global_memory
        WHERE id = ?
    """, (memory_id,))

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted > 0


# ---------------- MEMORY SUGGESTION FUNCTIONS ----------------

def save_memory_suggestion(
    memory,
    category="general",
    source_conversation_id=None
):
    memory = " ".join(memory.strip().split())

    if not memory:
        return None

    normalized_memory = memory.lower()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO memory_suggestions
        (memory, normalized_memory, category, source_conversation_id)
        VALUES (?, ?, ?, ?)
    """, (
        memory,
        normalized_memory,
        category,
        source_conversation_id
    ))

    cursor.execute("""
        SELECT id
        FROM memory_suggestions
        WHERE normalized_memory = ?
    """, (normalized_memory,))

    result = cursor.fetchone()

    connection.commit()
    connection.close()

    return result[0] if result else None


def reactivate_memory_suggestion(
    memory,
    category="general",
    source_conversation_id=None
):
    memory = " ".join(memory.strip().split())

    if not memory:
        return None

    normalized_memory = memory.lower()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, status
        FROM memory_suggestions
        WHERE normalized_memory = ?
    """, (normalized_memory,))

    existing = cursor.fetchone()

    if existing:
        suggestion_id = existing[0]

        if existing[1] == "dismissed":
            cursor.execute("""
                UPDATE memory_suggestions
                SET status = 'pending',
                    source_conversation_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (source_conversation_id, suggestion_id))

    else:
        cursor.execute("""
            INSERT INTO memory_suggestions
            (memory, normalized_memory, category, source_conversation_id)
            VALUES (?, ?, ?, ?)
        """, (
            memory,
            normalized_memory,
            category,
            source_conversation_id
        ))

        suggestion_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return suggestion_id



def get_pending_memory_suggestions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, memory, category, source_conversation_id, created_at
        FROM memory_suggestions
        WHERE status = 'pending'
        ORDER BY id DESC
    """)

    suggestions = cursor.fetchall()

    connection.close()

    return suggestions


def get_all_memory_suggestions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory,
            category,
            source_conversation_id,
            status
        FROM memory_suggestions
        ORDER BY id DESC
    """)

    suggestions = cursor.fetchall()
    connection.close()

    return suggestions


def update_memory_suggestion_status(suggestion_id, status):

    allowed_statuses = {"pending", "saved", "dismissed"}

    if status not in allowed_statuses:
        raise ValueError("Invalid memory suggestion status.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE memory_suggestions
        SET status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, suggestion_id))

    connection.commit()
    connection.close()

