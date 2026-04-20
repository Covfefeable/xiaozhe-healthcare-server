from flask import request

from app.services.auth import AuthError, AuthService
from app.utils.response import error_response, success_response


def phone_login():
    try:
        data = AuthService.login_by_phone(request.get_json(silent=True) or {})
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def wechat_login():
    try:
        data = AuthService.login_by_wechat(request.get_json(silent=True) or {})
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def me():
    try:
        user = AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=AuthService.serialize_user(user))


def update_me():
    try:
        user = AuthService.get_current_user(request.headers.get("Authorization"))
        data = AuthService.update_profile(user, request.get_json(silent=True) or {})
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data, message="保存成功")
