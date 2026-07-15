from flask import Flask

from config import config
from app.extensions import db, migrate, cors
import app.models  # noqa: F401


def create_app(config_class=config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
