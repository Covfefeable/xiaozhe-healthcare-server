from app.controllers import departments

from . import api_bp


@api_bp.get("/departments")
def list_departments():
    return departments.list_departments()
