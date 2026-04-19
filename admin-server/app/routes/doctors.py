from app.controllers import doctors

from . import api_bp


@api_bp.get("/doctors")
def list_doctors():
    return doctors.list_doctors()


@api_bp.post("/doctors")
def create_doctor():
    return doctors.create_doctor()


@api_bp.get("/doctors/<int:doctor_id>")
def get_doctor(doctor_id: int):
    return doctors.get_doctor(doctor_id)


@api_bp.put("/doctors/<int:doctor_id>")
def update_doctor(doctor_id: int):
    return doctors.update_doctor(doctor_id)


@api_bp.delete("/doctors/<int:doctor_id>")
def delete_doctor(doctor_id: int):
    return doctors.delete_doctor(doctor_id)
