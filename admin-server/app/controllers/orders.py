from flask import request

from app.services.auth import AuthError, AuthService
from app.services.orders import OrderError, OrderService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_orders():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = OrderService.list_orders(request.args)
    except OrderError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_order(order_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        order = OrderService.get_order(order_id)
    except OrderError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=OrderService.serialize(order))


def update_status(order_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        order = OrderService.update_status(order_id, (request.get_json(silent=True) or {}).get("status"))
    except OrderError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=OrderService.serialize(order), message="保存成功")
