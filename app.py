# Main Streamlit app — UI, sidebar, chat display, and conversation management
import streamlit as st
from sqlalchemy import desc

from config import HF_TOKEN
from db import SessionLocal
from models import Conversation, Message
from services.chat_service import chat

st.set_page_config(page_title="AI Chatbot", page_icon="💬", layout="wide")

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if not HF_TOKEN:
    st.error("Please set HF_TOKEN in your .env file.")
    st.stop()


def get_conversations():
    session = SessionLocal()
    try:
        return (
            session.query(Conversation)
            .order_by(desc(Conversation.updated_at))
            .all()
        )
    finally:
        session.close()


def get_messages(conversation_id: int):
    session = SessionLocal()
    try:
        return (
            session.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at)
            .all()
        )
    finally:
        session.close()


def create_conversation(title: str = "New Conversation") -> int:
    session = SessionLocal()
    try:
        conv = Conversation(title=title)
        session.add(conv)
        session.commit()
        return conv.id
    finally:
        session.close()


def delete_conversation(conversation_id: int):
    session = SessionLocal()
    try:
        conv = session.query(Conversation).get(conversation_id)
        if conv:
            session.delete(conv)
            session.commit()
    finally:
        session.close()


def conversation_exists(conversation_id: int) -> bool:
    session = SessionLocal()
    try:
        return session.query(Conversation).get(conversation_id) is not None
    finally:
        session.close()


with st.sidebar:
    st.title("💬 AI Chatbot")

    if st.button("+ New Chat", use_container_width=True):
        conv_id = create_conversation()
        st.session_state.current_conversation_id = conv_id
        st.rerun()

    st.divider()

    conversations = get_conversations()

    for conv in conversations:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(
                conv.title,
                key=f"conv_{conv.id}",
                use_container_width=True,
                type=(
                    "primary"
                    if conv.id == st.session_state.current_conversation_id
                    else "secondary"
                ),
            ):
                st.session_state.current_conversation_id = conv.id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv.id}"):
                delete_conversation(conv.id)
                if st.session_state.current_conversation_id == conv.id:
                    st.session_state.current_conversation_id = None
                st.rerun()


if st.session_state.current_conversation_id:
    if not conversation_exists(st.session_state.current_conversation_id):
        st.session_state.current_conversation_id = None
        st.rerun()

    messages = get_messages(st.session_state.current_conversation_id)

    for msg in messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    if prompt := st.chat_input("Type your message..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = chat(st.session_state.current_conversation_id, prompt)
                    st.markdown(reply)
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.stop()

        st.rerun()
else:
    st.markdown("### Welcome to AI Chatbot!")
    st.markdown("Click **+ New Chat** in the sidebar to start a conversation.")
