from flask import request

from app.services.auth import AuthError, AuthService
from app.services.orders import OrderError, OrderService
from app.utils.response import error_response, success_response


def _current_user():
    return AuthService.get_current_user(request.headers.get("Authorization"))


def create_order():
    try:
        user = _current_user()
        order = OrderService.create_from_cart(user, request.get_json(silent=True) or {})
    except (AuthError, OrderError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=order)


def create_direct_order():
    try:
        user = _current_user()
        order = OrderService.create_direct(user, request.get_json(silent=True) or {})
    except (AuthError, OrderError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=order)


def list_orders():
    try:
        user = _current_user()
        items = OrderService.list_orders(user, request.args)
    except (AuthError, OrderError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data={"items": items})


def get_order(order_id: int):
    try:
        user = _current_user()
        order = OrderService.get_order(user, order_id)
    except (AuthError, OrderError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=order)


def pay_order(order_id: int):
    try:
        user = _current_user()
        order = OrderService.pay_order(user, order_id)
    except (AuthError, OrderError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=order, message="支付成功")


def cancel_order(order_id: int):
    try:
        user = _current_user()
        OrderService.cancel_order(user, order_id)
    except (AuthError, OrderError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="取消成功")


def request_refund(order_id: int):
    try:
        user = _current_user()
        order = OrderService.request_refund(user, order_id, request.get_json(silent=True) or {})
    except (AuthError, OrderError) as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=order, message="退款申请已提交")
