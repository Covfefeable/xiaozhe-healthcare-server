from app.extensions import db
from app.models import Department, Doctor, MiniappUser


class DoctorError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


def _normalize_image_src(image: str | None) -> str:
    return image or ""


class DoctorService:
    @staticmethod
    def serialize(doctor: Doctor, include_phone: bool = False) -> dict:
        department_name = doctor.department.name if doctor.department else ""
        data = {
            "id": str(doctor.id),
            "department": str(doctor.department_id),
            "department_id": str(doctor.department_id),
            "departmentLabel": department_name,
            "department_name": department_name,
            "avatarUrl": _normalize_image_src(doctor.avatar_url),
            "avatar": _normalize_image_src(doctor.avatar_url),
            "name": doctor.name,
            "title": doctor.title or "",
            "hospital": doctor.hospital or "",
            "summary": doctor.summary or "",
            "specialties": doctor.specialty_tags or [],
            "specialty_tags": doctor.specialty_tags or [],
            "introduction": doctor.introduction or "",
        }
        if include_phone:
            data["phone"] = doctor.phone
        return data

    @staticmethod
    def list_doctors(args) -> list[dict]:
        keyword = (args.get("keyword") or "").strip()
        department_id = args.get("department_id")
        query = Doctor.query.join(Department).filter(
            Doctor.deleted_at.is_(None),
            Department.deleted_at.is_(None),
        )
        if department_id and department_id != "all":
            try:
                query = query.filter(Doctor.department_id == int(department_id))
            except (TypeError, ValueError):
                raise DoctorError("科室参数不正确") from None
        if keyword:
            query = query.filter(
                db.or_(
                    Doctor.name.ilike(f"%{keyword}%"),
                    Doctor.title.ilike(f"%{keyword}%"),
                    Doctor.hospital.ilike(f"%{keyword}%"),
                    Doctor.summary.ilike(f"%{keyword}%"),
                    Department.name.ilike(f"%{keyword}%"),
                )
            )
        items = query.order_by(Doctor.sort_order.asc(), Doctor.created_at.desc()).all()
        return [DoctorService.serialize(item) for item in items]

    @staticmethod
    def get_doctor(doctor_id: int) -> dict:
        doctor = Doctor.query.filter(Doctor.id == doctor_id, Doctor.deleted_at.is_(None)).first()
        if not doctor or doctor.department.deleted_at is not None:
            raise DoctorError("医生不存在", 404)
        return DoctorService.serialize(doctor)

    @staticmethod
    def get_current_doctor(user: MiniappUser) -> dict:
        phone = (user.phone or "").strip()
        if not phone:
            raise DoctorError("当前登录用户未绑定手机号", 404)
        doctor = Doctor.query.join(Department).filter(
            Doctor.phone == phone,
            Doctor.deleted_at.is_(None),
            Department.deleted_at.is_(None),
        ).first()
        if not doctor:
            raise DoctorError("当前手机号未匹配到医生信息", 404)
        return DoctorService.serialize(doctor, include_phone=True)
