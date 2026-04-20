from app.extensions import db
from app.models import Department, Doctor
from app.utils.time import beijing_iso


class DoctorError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class DoctorService:
    @staticmethod
    def serialize(doctor: Doctor, include_phone: bool = True) -> dict:
        data = {
            "id": doctor.id,
            "department_id": doctor.department_id,
            "department_name": doctor.department.name if doctor.department else "",
            "avatar_url": doctor.avatar_url or "",
            "name": doctor.name,
            "title": doctor.title or "",
            "hospital": doctor.hospital or "",
            "summary": doctor.summary or "",
            "specialty_tags": doctor.specialty_tags or [],
            "introduction": doctor.introduction or "",
            "sort_order": doctor.sort_order,
            "created_at": beijing_iso(doctor.created_at),
            "updated_at": beijing_iso(doctor.updated_at),
        }
        if include_phone:
            data["phone"] = doctor.phone
        return data

    @staticmethod
    def list_doctors(args) -> dict:
        page = DoctorService._positive_int(args.get("page"), default=1)
        page_size = DoctorService._positive_int(args.get("page_size"), default=20, maximum=100)
        keyword = (args.get("keyword") or "").strip()
        department_id = args.get("department_id")
        query = Doctor.query.join(Department).filter(
            Doctor.deleted_at.is_(None),
            Department.deleted_at.is_(None),
        )
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
        if department_id:
            try:
                query = query.filter(Doctor.department_id == int(department_id))
            except (TypeError, ValueError):
                raise DoctorError("科室参数不正确") from None
        total = query.count()
        items = (
            query.order_by(Doctor.sort_order.asc(), Doctor.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [DoctorService.serialize(item) for item in items],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }

    @staticmethod
    def get_doctor(doctor_id: int) -> Doctor:
        doctor = Doctor.query.filter(Doctor.id == doctor_id, Doctor.deleted_at.is_(None)).first()
        if not doctor or doctor.department.deleted_at is not None:
            raise DoctorError("医生不存在", 404)
        return doctor

    @staticmethod
    def create_doctor(data: dict) -> Doctor:
        doctor = Doctor(**DoctorService._validate_payload(data))
        db.session.add(doctor)
        db.session.commit()
        return doctor

    @staticmethod
    def update_doctor(doctor_id: int, data: dict) -> Doctor:
        doctor = DoctorService.get_doctor(doctor_id)
        payload = DoctorService._validate_payload(data, doctor_id=doctor_id)
        for key, value in payload.items():
            setattr(doctor, key, value)
        db.session.commit()
        return doctor

    @staticmethod
    def delete_doctor(doctor_id: int) -> None:
        doctor = DoctorService.get_doctor(doctor_id)
        doctor.soft_delete()
        db.session.commit()

    @staticmethod
    def _validate_payload(data: dict, doctor_id: int | None = None) -> dict:
        try:
            department_id = int(data.get("department_id"))
        except (TypeError, ValueError):
            raise DoctorError("请选择所属科室") from None
        department = Department.query.filter(
            Department.id == department_id,
            Department.deleted_at.is_(None),
        ).first()
        if not department:
            raise DoctorError("所属科室不存在")

        name = (data.get("name") or "").strip()
        if not name:
            raise DoctorError("医生姓名不能为空")
        if len(name) > 50:
            raise DoctorError("医生姓名不能超过 50 个字符")
        phone = (data.get("phone") or "").strip()
        if not phone:
            raise DoctorError("手机号码不能为空")
        if len(phone) > 20:
            raise DoctorError("手机号码不能超过 20 个字符")
        duplicate_query = Doctor.query.filter(
            Doctor.phone == phone,
            Doctor.deleted_at.is_(None),
        )
        if doctor_id is not None:
            duplicate_query = duplicate_query.filter(Doctor.id != doctor_id)
        if duplicate_query.first():
            raise DoctorError("该手机号已存在医生信息")
        title = (data.get("title") or "").strip()
        hospital = (data.get("hospital") or "").strip()
        summary = (data.get("summary") or "").strip()
        introduction = data.get("introduction") or ""
        if len(title) > 50:
            raise DoctorError("职称不能超过 50 个字符")
        if len(hospital) > 100:
            raise DoctorError("医院不能超过 100 个字符")
        if len(summary) > 120:
            raise DoctorError("列表简介不能超过 120 个字符")
        return {
            "department_id": department_id,
            "avatar_url": data.get("avatar_url") or "",
            "name": name,
            "phone": phone,
            "title": title,
            "hospital": hospital,
            "summary": summary,
            "specialty_tags": DoctorService._parse_tags(data.get("specialty_tags")),
            "introduction": introduction,
            "sort_order": DoctorService._int_or_default(data.get("sort_order"), 0),
        }

    @staticmethod
    def _parse_tags(value) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

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
