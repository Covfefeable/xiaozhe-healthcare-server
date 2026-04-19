from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis


db = SQLAlchemy()
migrate = Migrate()


def init_extensions(app) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    app.extensions["redis"] = Redis.from_url(app.config["REDIS_URL"])
