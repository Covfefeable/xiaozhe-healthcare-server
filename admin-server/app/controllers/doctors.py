from flask import request

from app.services.auth import AuthError, AuthService
from app.services.doctors import DoctorError, DoctorService
from app.utils.response import error_response, success_response


def _require_auth():
    try:
        AuthService.get_current_user(request.headers.get("Authorization"))
    except AuthError as exc:
        return error_response(message=exc.message, code=exc.code)
    return None


def list_doctors():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        data = DoctorService.list_doctors(request.args)
    except DoctorError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=data)


def get_doctor(doctor_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        doctor = DoctorService.get_doctor(doctor_id)
    except DoctorError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=DoctorService.serialize(doctor))


def create_doctor():
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        doctor = DoctorService.create_doctor(request.get_json(silent=True) or {})
    except DoctorError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=DoctorService.serialize(doctor), message="创建成功", status_code=201)


def update_doctor(doctor_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        doctor = DoctorService.update_doctor(doctor_id, request.get_json(silent=True) or {})
    except DoctorError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=DoctorService.serialize(doctor), message="保存成功")


def delete_doctor(doctor_id: int):
    auth_error = _require_auth()
    if auth_error:
        return auth_error
    try:
        DoctorService.delete_doctor(doctor_id)
    except DoctorError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=None, message="删除成功")
