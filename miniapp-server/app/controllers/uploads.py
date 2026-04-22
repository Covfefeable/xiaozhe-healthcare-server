from flask import request

from app.services.auth import AuthError, AuthService
from app.services.storage import StorageError, StorageService
from app.utils.response import error_response, success_response


def upload_file():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
        data = StorageService.upload_file(request.files.get("file"), request.form.get("biz_type") or "")
    except (AuthError, StorageError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data, message="上传成功")
