import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace-this-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/xiaozhe_medical",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ALEMBIC_VERSION_TABLE = os.getenv(
        "ALEMBIC_VERSION_TABLE",
        "admin_alembic_version",
    )
    DB_TABLE_PREFIX = os.getenv("DB_TABLE_PREFIX", "admin_")
    JSON_AS_ASCII = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
