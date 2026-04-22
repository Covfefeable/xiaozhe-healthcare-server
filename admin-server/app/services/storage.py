from datetime import datetime
from pathlib import Path
from uuid import uuid4

import oss2
from flask import current_app


class StorageError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


BIZ_TYPE_DIRS = {
    "product": "products",
    "banner": "banners",
    "news": "news",
    "markdown": "markdown",
    "doctor_avatar": "avatars/doctors",
    "assistant_avatar": "avatars/assistants",
    "customer_service_avatar": "avatars/customer-services",
}

MARKDOWN_SIGNED_URL_EXPIRES = 3650 * 24 * 60 * 60


class StorageService:
    @staticmethod
    def upload_file(file, biz_type: str) -> dict:
        if not file or not file.filename:
            raise StorageError("请选择要上传的文件")
        content = file.read()
        max_size = current_app.config["OSS_UPLOAD_MAX_SIZE_MB"] * 1024 * 1024
        if len(content) > max_size:
            raise StorageError("文件大小超过限制")

        object_key = StorageService._build_object_key(file.filename, biz_type)
        StorageService._bucket().put_object(object_key, content)
        signed_url_expires = MARKDOWN_SIGNED_URL_EXPIRES if biz_type == "markdown" else None
        return {
            "object_key": object_key,
            "url": StorageService.sign_url(object_key, signed_url_expires),
            "file_name": file.filename,
            "mime_type": file.mimetype or "",
            "size": len(content),
        }

    @staticmethod
    def sign_url(object_key: str | None, expires: int | None = None) -> str:
        if not object_key:
            return ""
        if object_key.startswith(("http://", "https://", "data:")):
            return object_key
        expires = expires or current_app.config["ALIYUN_OSS_SIGNED_URL_EXPIRES"]
        return StorageService._bucket().sign_url("GET", object_key, expires, slash_safe=True)

    @staticmethod
    def sign_urls(object_keys) -> list[str]:
        return [StorageService.sign_url(item) for item in object_keys or [] if item]

    @staticmethod
    def delete_file(object_key: str | None) -> None:
        if object_key:
            StorageService._bucket().delete_object(object_key)

    @staticmethod
    def _build_object_key(filename: str, biz_type: str) -> str:
        directory = BIZ_TYPE_DIRS.get(biz_type)
        if not directory:
            raise StorageError("上传业务类型不正确")
        suffix = Path(filename).suffix.lower()
        today = datetime.utcnow()
        prefix = current_app.config["OSS_OBJECT_PREFIX"]
        parts = [part for part in [prefix, directory, f"{today:%Y/%m/%d}", f"{uuid4().hex}{suffix}"] if part]
        return "/".join(parts)

    @staticmethod
    def _bucket():
        required = [
            "ALIYUN_OSS_ACCESS_KEY_ID",
            "ALIYUN_OSS_ACCESS_KEY_SECRET",
            "ALIYUN_OSS_ENDPOINT",
            "ALIYUN_OSS_BUCKET",
        ]
        if any(not current_app.config.get(key) for key in required):
            raise StorageError("阿里云 OSS 配置不完整", 500)
        auth = oss2.Auth(
            current_app.config["ALIYUN_OSS_ACCESS_KEY_ID"],
            current_app.config["ALIYUN_OSS_ACCESS_KEY_SECRET"],
        )
        return oss2.Bucket(
            auth,
            current_app.config["ALIYUN_OSS_ENDPOINT"],
            current_app.config["ALIYUN_OSS_BUCKET"],
        )
