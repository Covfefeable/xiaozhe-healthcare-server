from app.models import Department


class DepartmentService:
    @staticmethod
    def serialize(department: Department) -> dict:
        return {
            "id": str(department.id),
            "key": str(department.id),
            "label": department.name,
            "name": department.name,
            "description": department.description or "",
            "sort_order": department.sort_order,
        }

    @staticmethod
    def list_departments() -> list[dict]:
        items = (
            Department.query.filter(Department.deleted_at.is_(None))
            .order_by(Department.sort_order.asc(), Department.created_at.desc())
            .all()
        )
        return [DepartmentService.serialize(item) for item in items]
