from app.extensions import db
from app.models import Department, Doctor
from app.utils.time import beijing_iso


class DepartmentError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class DepartmentService:
    @staticmethod
    def serialize(department: Department) -> dict:
        return {
            "id": department.id,
            "name": department.name,
            "description": department.description or "",
            "sort_order": department.sort_order,
            "created_at": beijing_iso(department.created_at),
            "updated_at": beijing_iso(department.updated_at),
        }

    @staticmethod
    def list_departments(args) -> dict:
        page = DepartmentService._positive_int(args.get("page"), default=1)
        page_size = DepartmentService._positive_int(args.get("page_size"), default=20, maximum=100)
        keyword = (args.get("keyword") or "").strip()
        query = Department.query.filter(Department.deleted_at.is_(None))
        if keyword:
            query = query.filter(Department.name.ilike(f"%{keyword}%"))
        total = query.count()
        items = (
            query.order_by(Department.sort_order.asc(), Department.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [DepartmentService.serialize(item) for item in items],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }

    @staticmethod
    def get_department(department_id: int) -> Department:
        department = Department.query.filter(
            Department.id == department_id,
            Department.deleted_at.is_(None),
        ).first()
        if not department:
            raise DepartmentError("科室不存在", 404)
        return department

    @staticmethod
    def create_department(data: dict) -> Department:
        department = Department(**DepartmentService._validate_payload(data))
        db.session.add(department)
        db.session.commit()
        return department

    @staticmethod
    def update_department(department_id: int, data: dict) -> Department:
        department = DepartmentService.get_department(department_id)
        payload = DepartmentService._validate_payload(data)
        for key, value in payload.items():
            setattr(department, key, value)
        db.session.commit()
        return department

    @staticmethod
    def delete_department(department_id: int) -> None:
        department = DepartmentService.get_department(department_id)
        doctor_count = Doctor.query.filter(
            Doctor.department_id == department.id,
            Doctor.deleted_at.is_(None),
        ).count()
        if doctor_count:
            raise DepartmentError("该科室下还有医生，不能删除")
        department.soft_delete()
        db.session.commit()

    @staticmethod
    def _validate_payload(data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise DepartmentError("科室名称不能为空")
        if len(name) > 50:
            raise DepartmentError("科室名称不能超过 50 个字符")
        description = (data.get("description") or "").strip()
        if len(description) > 255:
            raise DepartmentError("科室简介不能超过 255 个字符")
        return {
            "name": name,
            "description": description,
            "sort_order": DepartmentService._int_or_default(data.get("sort_order"), 0),
        }

    @staticmethod
    def _positive_int(value, default: int, maximum: int | None = None) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = default
        if number < 1:
            number = default
        if maximum is not None:
            number = min(number, maximum)
        return number

    @staticmethod
    def _int_or_default(value, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
