import os

from dotenv import load_dotenv
from flask import Flask

from .config import config_by_name
from .extensions import init_extensions
from .routes import register_blueprints


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)

    selected_config = config_name or os.getenv("APP_ENV", "development")
    app.config.from_object(config_by_name[selected_config])

    from . import models  # noqa: F401

    init_extensions(app)
    register_blueprints(app)

    return app
