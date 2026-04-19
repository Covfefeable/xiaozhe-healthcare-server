from flask import request

from app.services.auth import AuthError, AuthService
from app.services.departments import DepartmentError, DepartmentService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_departments():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = DepartmentService.list_departments(request.args)
    except DepartmentError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_department(department_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        department = DepartmentService.get_department(department_id)
    except DepartmentError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=DepartmentService.serialize(department))


def create_department():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        department = DepartmentService.create_department(request.get_json(silent=True) or {})
    except DepartmentError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=DepartmentService.serialize(department), message="创建成功", status_code=201)


def update_department(department_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        department = DepartmentService.update_department(department_id, request.get_json(silent=True) or {})
    except DepartmentError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=DepartmentService.serialize(department), message="保存成功")


def delete_department(department_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        DepartmentService.delete_department(department_id)
    except DepartmentError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="删除成功")
