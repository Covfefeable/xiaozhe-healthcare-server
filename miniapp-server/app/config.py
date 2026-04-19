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
        "miniapp_alembic_version",
    )
    DB_TABLE_PREFIX = os.getenv("DB_TABLE_PREFIX", "miniapp_")
    JSON_AS_ASCII = False
    MINIAPP_TOKEN_EXPIRES = int(os.getenv("MINIAPP_TOKEN_EXPIRES", "604800"))
    WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
    WECHAT_API_TIMEOUT = int(os.getenv("WECHAT_API_TIMEOUT", "8"))


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
