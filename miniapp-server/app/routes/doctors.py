from app.controllers import doctors

from . import api_bp


@api_bp.get("/doctors")
def list_doctors():
    return doctors.list_doctors()


@api_bp.get("/doctors/me")
def get_current_doctor():
    return doctors.get_current_doctor()


@api_bp.get("/doctors/<int:doctor_id>")
def get_doctor(doctor_id: int):
    return doctors.get_doctor(doctor_id)
