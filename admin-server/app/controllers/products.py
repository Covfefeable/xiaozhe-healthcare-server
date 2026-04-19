from flask import request

from app.services.auth import AuthError, AuthService
from app.services.products import ProductError, ProductService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_products():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = ProductService.list_products(request.args)
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_product(product_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        product = ProductService.get_product(product_id)
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=ProductService.serialize(product))


def create_product():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        product = ProductService.create_product(request.get_json(silent=True) or {})
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(
        data=ProductService.serialize(product),
        message="创建成功",
        status_code=201,
    )


def update_product(product_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        product = ProductService.update_product(
            product_id,
            request.get_json(silent=True) or {},
        )
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=ProductService.serialize(product), message="保存成功")


def delete_product(product_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        ProductService.delete_product(product_id)
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="删除成功")


def publish_product(product_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        product = ProductService.publish_product(product_id)
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=ProductService.serialize(product), message="上架成功")


def unpublish_product(product_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        product = ProductService.unpublish_product(product_id)
    except ProductError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=ProductService.serialize(product), message="下架成功")
