from app.controllers import departments

from . import api_bp


@api_bp.get("/departments")
def list_departments():
    return departments.list_departments()


@api_bp.post("/departments")
def create_department():
    return departments.create_department()


@api_bp.get("/departments/<int:department_id>")
def get_department(department_id: int):
    return departments.get_department(department_id)


@api_bp.put("/departments/<int:department_id>")
def update_department(department_id: int):
    return departments.update_department(department_id)


@api_bp.delete("/departments/<int:department_id>")
def delete_department(department_id: int):
    return departments.delete_department(department_id)
