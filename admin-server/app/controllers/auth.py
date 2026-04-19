from flask import current_app, request

from app.services.auth import AuthError, AuthService
from app.utils.response import error_response, success_response


def register():
    try:
        user = AuthService.register(request.get_json(silent=True) or {})
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)

    return success_response(
        data=AuthService.serialize_user(user),
        message="注册成功",
        code=201,
    )


def login():
    data = request.get_json(silent=True) or {}
    try:
        result = AuthService.login(data.get("username"), data.get("password"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)

    return success_response(data=result, message="登录成功")


def me():
    try:
        user = AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)

    return success_response(data=AuthService.serialize_user(user))


def logout():
    return success_response(message="退出成功")


def config():
    return success_response(data={"allow_register": current_app.config["ALLOW_REGISTER"]})
