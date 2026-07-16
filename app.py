# Main Streamlit app — UI, sidebar, chat display, and conversation management
import streamlit as st
from sqlalchemy import desc

from config import HF_TOKEN
from db import SessionLocal
from models import Conversation, Message
from services.chat_service import chat

# Page config — sets the browser tab title and layout
st.set_page_config(page_title="AI Chatbot", page_icon="💬", layout="wide")

# Track which conversation is currently open (stored in browser session)
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

# Stop app if no API key is configured
if not HF_TOKEN:
    st.error("Please set HF_TOKEN in your .env file.")
    st.stop()


def get_conversations():
    """Fetch all conversations from DB, sorted by most recently updated first."""
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
    """Fetch all messages for a specific conversation, in chronological order."""
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
    """Create a new conversation in DB and return its ID."""
    session = SessionLocal()
    try:
        conv = Conversation(title=title)
        session.add(conv)
        session.commit()
        return conv.id
    finally:
        session.close()


def delete_conversation(conversation_id: int):
    """Delete a conversation and all its messages from DB (cascade delete)."""
    session = SessionLocal()
    try:
        conv = session.query(Conversation).get(conversation_id)
        if conv:
            session.delete(conv)
            session.commit()
    finally:
        session.close()


def conversation_exists(conversation_id: int) -> bool:
    """Check if a conversation still exists in DB (handles deleted conversations)."""
    session = SessionLocal()
    try:
        return session.query(Conversation).get(conversation_id) is not None
    finally:
        session.close()


# --- SIDEBAR: conversation list + new chat button ---
with st.sidebar:
    st.title("💬 AI Chatbot")

    # Button to create a new conversation
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.current_conversation_id = None
        st.session_state.pending_new_chat = True
        st.rerun()

    st.divider()

    # List all conversations with switch and delete buttons
    conversations = get_conversations()

    for conv in conversations:
        col1, col2 = st.columns([5, 1])
        with col1:
            # Click to switch to this conversation
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
                st.session_state.pending_new_chat = False
                st.rerun()
        with col2:
            # Delete button for each conversation
            if st.button("🗑️", key=f"del_{conv.id}"):
                delete_conversation(conv.id)
                if st.session_state.current_conversation_id == conv.id:
                    st.session_state.current_conversation_id = None
                st.rerun()


# --- MAIN CHAT AREA ---
if st.session_state.current_conversation_id:
    # Safety check — if conversation was deleted elsewhere, reset to welcome screen
    if not conversation_exists(st.session_state.current_conversation_id):
        st.session_state.current_conversation_id = None
        st.rerun()

    # Display all previous messages in the chat area
    messages = get_messages(st.session_state.current_conversation_id)

    for msg in messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    # Text input at the bottom — user types and sends a message
    if prompt := st.chat_input("Type your message..."):
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send to AI, show reply, save both to DB
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = chat(st.session_state.current_conversation_id, prompt)
                    st.markdown(reply)
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.stop()

        # Refresh page to update sidebar (conversation title, message list)
        st.rerun()
else:
    # Welcome screen when no conversation is selected
    st.markdown("### Welcome to AI Chatbot!")
    if st.session_state.get("pending_new_chat"):
        # Show chat input for new conversation — conversation created on first message
        if prompt := st.chat_input("Type your message..."):
            conv_id = create_conversation()
            st.session_state.current_conversation_id = conv_id
            st.session_state.pending_new_chat = False
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        reply = chat(conv_id, prompt)
                        st.markdown(reply)
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.stop()
            st.rerun()
    else:
        st.markdown("Click **+ New Chat** in the sidebar to start a conversation.")
