from flask import request

from app.services.auth import AuthError, AuthService
from app.services.banners import BannerError, BannerService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_banners():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = BannerService.list_banners(request.args)
    except BannerError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_banner(banner_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        banner = BannerService.get_banner(banner_id)
    except BannerError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=BannerService.serialize(banner))


def create_banner():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        banner = BannerService.create_banner(request.get_json(silent=True) or {})
    except BannerError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(
        data=BannerService.serialize(banner),
        message="创建成功",
        status_code=201,
    )


def update_banner(banner_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        banner = BannerService.update_banner(banner_id, request.get_json(silent=True) or {})
    except BannerError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=BannerService.serialize(banner), message="保存成功")


def delete_banner(banner_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        BannerService.delete_banner(banner_id)
    except BannerError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="删除成功")
