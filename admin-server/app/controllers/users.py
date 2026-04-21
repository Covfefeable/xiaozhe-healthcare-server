from flask import request

from app.services.auth import AuthError, AuthService
from app.services.users import UserError, UserService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_users():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    data = UserService.list_users(request.args)
    return success_response(data=data)


def get_user(user_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = UserService.get_user(user_id)
    except UserError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def renew_membership(user_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = UserService.renew_membership(user_id, request.get_json(silent=True) or {})
    except UserError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data, message="续期成功")
