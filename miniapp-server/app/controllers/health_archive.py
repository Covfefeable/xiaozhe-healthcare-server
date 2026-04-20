from flask import request

from app.services.auth import AuthError, AuthService
from app.services.health_archive import HealthArchiveError, HealthArchiveService
from app.utils.response import error_response, success_response


def _current_user():
    return AuthService.get_current_user(request.headers.get("Authorization"))


def get_my_archive():
    try:
        user = _current_user()
        data = HealthArchiveService.get_archive(user)
    except (AuthError, HealthArchiveError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def update_my_archive():
    try:
        user = _current_user()
        data = HealthArchiveService.update_archive(user, request.get_json(silent=True) or {})
    except (AuthError, HealthArchiveError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data, message="保存成功")


def get_conversation_user_archive(conversation_id: int):
    try:
        user = _current_user()
        data = HealthArchiveService.get_archive_by_conversation(
            user,
            conversation_id,
            request.args.get("role") or "doctor",
        )
    except (AuthError, HealthArchiveError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)
