from flask import request

from app.services.auth import AuthError, AuthService
from app.services.staff import AssistantService, CustomerServiceService, StaffError
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def _service(kind: str):
    return AssistantService if kind == "assistant" else CustomerServiceService


def list_staff(kind: str):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = _service(kind).list_items(request.args)
    except StaffError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_staff(kind: str, item_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    service = _service(kind)
    try:
        item = service.get_item(item_id)
    except StaffError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=service.serialize(item))


def create_staff(kind: str):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    service = _service(kind)
    try:
        item = service.create_item(request.get_json(silent=True) or {})
    except StaffError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=service.serialize(item), message="创建成功", status_code=201)


def update_staff(kind: str, item_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    service = _service(kind)
    try:
        item = service.update_item(item_id, request.get_json(silent=True) or {})
    except StaffError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=service.serialize(item), message="保存成功")


def delete_staff(kind: str, item_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        _service(kind).delete_item(item_id)
    except StaffError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="删除成功")
