# Hugging Face chat service — sends messages to the AI and saves to DB
from huggingface_hub import InferenceClient

from config import HF_TOKEN
from db import SessionLocal
from models import Conversation, Message

# System prompt sent to the AI at the start of every conversation
SYSTEM_PROMPT = "You are a helpful assistant."

# The free Hugging Face model we're using for chat
MODEL = "Qwen/Qwen2.5-7B-Instruct"

# Singleton Hugging Face client — created once and reused
_client = None


def _get_client() -> InferenceClient:
    """Create and cache the Hugging Face InferenceClient (created once, reused)."""
    global _client
    if _client is None:
        _client = InferenceClient(token=HF_TOKEN)
    return _client


def chat(conversation_id: int, user_message: str) -> str:
    """
    Main chat function — does 4 things:
    1. Loads previous messages from DB for this conversation
    2. Sends all messages to the Hugging Face AI model
    3. Saves both user message and AI reply to DB
    4. Renames conversation to first message if it's a new chat
    """
    session = SessionLocal()

    # Step 1: Load chat history from database for this conversation
    history = (
        session.query(Message)
        .filter_by(conversation_id=conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    # Step 2: Build message list and send to AI
    # Start with system prompt, add all previous messages, then current user message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": user_message})

    # Call Hugging Face API to get AI response
    response = _get_client().chat_completion(
        model=MODEL,
        messages=messages,
        max_tokens=1024,
    )

    # Extract the AI's reply text
    assistant_reply = response.choices[0].message.content

    # Step 3: Save both user message and AI reply to database
    session.add(Message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
    ))
    session.add(Message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_reply,
    ))
    session.commit()

    # Step 4: If this is the first message, rename conversation to show the prompt
    if not history:
        title = user_message[:50]
        if len(user_message) > 50:
            title += "..."
        conv = session.query(Conversation).get(conversation_id)
        if conv:
            conv.title = title
            session.commit()

    return assistant_reply
