from fastapi import FastAPI

from config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="AI Chatbot")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
