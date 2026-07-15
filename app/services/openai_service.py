from openai import OpenAI

from config import config
from app.extensions import db
from app.models import Message

_client = None

SYSTEM_PROMPT = "You are a helpful assistant."


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def chat(conversation_id: int, user_message: str) -> str:
    history = (
        Message.query
        .filter_by(conversation_id=conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": user_message})

    response = _get_client().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    assistant_reply = response.choices[0].message.content

    db.session.add(Message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
    ))
    db.session.add(Message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_reply,
    ))
    db.session.commit()

    return assistant_reply
