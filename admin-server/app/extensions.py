from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis


db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


def init_extensions(app) -> None:
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    migrate.init_app(
        app,
        db,
        compare_type=True,
        version_table=app.config["ALEMBIC_VERSION_TABLE"],
    )
    app.extensions["redis"] = Redis.from_url(app.config["REDIS_URL"])
