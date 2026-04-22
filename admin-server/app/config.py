import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace-this-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "7200"))
    ALLOW_REGISTER = os.getenv("ALLOW_REGISTER", "false").lower() == "true"
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
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
