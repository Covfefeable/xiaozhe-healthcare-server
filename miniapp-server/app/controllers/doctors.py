from flask import request

from app.services.doctors import DoctorError, DoctorService
from app.utils.response import error_response, success_response


def list_doctors():
    try:
        items = DoctorService.list_doctors(request.args)
    except DoctorError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data={"items": items})


def get_doctor(doctor_id: int):
    try:
        doctor = DoctorService.get_doctor(doctor_id)
    except DoctorError as exc:
        return error_response(message=exc.message, code=exc.code)
    return success_response(data=doctor)
