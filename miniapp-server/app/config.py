import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace-this-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/xiaozhe_medical",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ALIYUN_OSS_ACCESS_KEY_ID = os.getenv("ALIYUN_OSS_ACCESS_KEY_ID", "")
    ALIYUN_OSS_ACCESS_KEY_SECRET = os.getenv("ALIYUN_OSS_ACCESS_KEY_SECRET", "")
    ALIYUN_OSS_ENDPOINT = os.getenv("ALIYUN_OSS_ENDPOINT", "")
    ALIYUN_OSS_BUCKET = os.getenv("ALIYUN_OSS_BUCKET", "")
    ALIYUN_OSS_REGION = os.getenv("ALIYUN_OSS_REGION", "")
    ALIYUN_OSS_SIGNED_URL_EXPIRES = int(os.getenv("ALIYUN_OSS_SIGNED_URL_EXPIRES", "900"))
    OSS_UPLOAD_MAX_SIZE_MB = int(os.getenv("OSS_UPLOAD_MAX_SIZE_MB", "20"))
    OSS_OBJECT_PREFIX = os.getenv("OSS_OBJECT_PREFIX", "dev").strip().strip("/")
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
