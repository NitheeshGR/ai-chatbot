from huggingface_hub import InferenceClient

from config import HF_TOKEN
from db import SessionLocal
from models import Message

SYSTEM_PROMPT = "You are a helpful assistant."

MODEL = "Qwen/Qwen2.5-7B-Instruct"

_client = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        _client = InferenceClient(token=HF_TOKEN)
    return _client


def chat(conversation_id: int, user_message: str) -> str:
    session = SessionLocal()
    history = (
        session.query(Message)
        .filter_by(conversation_id=conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": user_message})

    response = _get_client().chat_completion(
        model=MODEL,
        messages=messages,
        max_tokens=1024,
    )

    assistant_reply = response.choices[0].message.content

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

    return assistant_reply
