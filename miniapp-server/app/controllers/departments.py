from app.services.departments import DepartmentService
from app.utils.response import success_response


def list_departments():
    items = [{"id": "all", "key": "all", "label": "全部科室", "name": "全部科室"}]
    items.extend(DepartmentService.list_departments())
    return success_response(data={"items": items})
