# AI Chatbot

A conversational AI chatbot web application built with Streamlit that connects to the Hugging Face Inference API. Supports multiple persistent conversations stored in a PostgreSQL database.

## Features

- **Chat with AI** — Powered by Qwen/Qwen2.5-7B-Instruct model via Hugging Face Serverless Inference API
- **Multiple Conversations** — Create, switch between, and delete conversations
- **Persistent Storage** — All chat history saved in PostgreSQL database
- **Auto-Titling** — Conversations automatically titled with first message
- **Retry Logic** — Automatic retry with exponential backoff for API timeouts/errors
- **Sidebar Navigation** — Easy conversation management with sorted list

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Backend** | Python |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Migrations** | Alembic |
| **AI Model** | Qwen/Qwen2.5-7B-Instruct (Hugging Face) |

## Project Structure

```
AI-Chatbot/
├── app.py                  # Main Streamlit application (UI + conversation management)
├── config.py               # Configuration loader (reads .env, exposes DATABASE_URL, HF_TOKEN)
├── db.py                   # SQLAlchemy engine, session factory, and Base class
├── models.py               # Database models: Conversation and Message
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not tracked by git)
├── .gitignore              # Git ignore rules
├── alembic.ini             # Alembic migration configuration
├── services/
│   ├── __init__.py
│   └── chat_service.py     # Hugging Face AI chat service with retry logic
└── migrations/
    ├── env.py              # Alembic environment config
    ├── script.py.mako      # Alembic migration template
    └── versions/
        └── dcd99c972f13_initial_migration.py
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd AI-Chatbot
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Create database
createdb ai_chatbot
```

### 5. Create Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_chatbot
HF_TOKEN=hf_your_huggingface_token_here
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

## Running the App

```bash
streamlit run app.py
```

The app will start at `http://localhost:8501`.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `HF_TOKEN` | Hugging Face API token | Yes |

Get your Hugging Face token at: https://huggingface.co/settings/tokens

## Database Schema

### conversations Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `title` | String(255) | Conversation title (auto-generated from first message) |
| `created_at` | DateTime | Creation timestamp (UTC) |
| `updated_at` | DateTime | Last update timestamp (UTC, auto-updates) |

### messages Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `conversation_id` | Integer | Foreign key to conversations table |
| `role` | String(20) | Message sender: "user" or "assistant" |
| `content` | Text | Message content |
| `created_at` | DateTime | Creation timestamp (UTC) |

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Rollback one migration step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| AI Model | Qwen/Qwen2.5-7B-Instruct | Hugging Face model |
| Max Tokens | 512 | Maximum response length |
| API Timeout | 60 seconds | Request timeout |
| Max Retries | 5 | Retry attempts with exponential backoff |

## How It Works

1. User clicks "+ New Chat" in sidebar
2. Chat input appears (conversation created only on first message)
3. User types message and sends
4. Message saved to database
5. AI generates response via Hugging Face API
6. Response saved to database
7. Conversation title set to first message (truncated to 50 chars)
8. Full chat history displayed when switching conversations

## License

This project is open source and available for personal use.

## Author

**NitheeshGR**
