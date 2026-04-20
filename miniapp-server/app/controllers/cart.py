from flask import request

from app.services.auth import AuthError, AuthService
from app.services.cart import CartError, CartService
from app.utils.response import error_response, success_response


def _current_user():
    return AuthService.get_current_user(request.headers.get("Authorization"))


def list_items():
    try:
        user = _current_user()
        data = CartService.list_items(user)
    except (AuthError, CartError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def add_item():
    try:
        user = _current_user()
        item = CartService.add_item(user, request.get_json(silent=True) or {})
    except (AuthError, CartError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=item, message="加入购物车成功")


def update_item(item_id: int):
    try:
        user = _current_user()
        item = CartService.update_item(user, item_id, request.get_json(silent=True) or {})
    except (AuthError, CartError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=item, message="保存成功")


def delete_item(item_id: int):
    try:
        user = _current_user()
        CartService.delete_item(user, item_id)
    except (AuthError, CartError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="删除成功")
