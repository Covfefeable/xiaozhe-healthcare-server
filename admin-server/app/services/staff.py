from app.extensions import db
from app.models import Assistant, CustomerService
from app.services.storage import StorageService
from app.utils.time import beijing_iso


class StaffError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


STAFF_STATUS = {"active", "inactive"}
ASSISTANT_TYPES = {"health_manager", "medical_assistant"}


class StaffService:
    model = None
    label = "人员"

    @classmethod
    def serialize(cls, item) -> dict:
        data = {
            "id": item.id,
            "avatar_object_key": item.avatar_object_key or "",
            "avatar_url": StorageService.sign_url(item.avatar_object_key),
            "name": item.name,
            "phone": item.phone,
            "status": item.status,
            "remark": item.remark or "",
            "created_at": beijing_iso(item.created_at),
            "updated_at": beijing_iso(item.updated_at),
        }
        if hasattr(item, "assistant_type"):
            data["assistant_type"] = item.assistant_type or "health_manager"
        return data

    @classmethod
    def list_items(cls, args) -> dict:
        page = cls._positive_int(args.get("page"), default=1)
        page_size = cls._positive_int(args.get("page_size"), default=20, maximum=100)
        keyword = (args.get("keyword") or "").strip()
        status = (args.get("status") or "").strip()
        query = cls.model.query.filter(cls.model.deleted_at.is_(None))
        if keyword:
            query = query.filter(
                db.or_(
                    cls.model.name.ilike(f"%{keyword}%"),
                    cls.model.phone.ilike(f"%{keyword}%"),
                    cls.model.remark.ilike(f"%{keyword}%"),
                )
            )
        if status:
            if status not in STAFF_STATUS:
                raise StaffError("状态参数不正确")
            query = query.filter(cls.model.status == status)
        assistant_type = (args.get("assistant_type") or "").strip()
        if assistant_type and hasattr(cls.model, "assistant_type"):
            if assistant_type not in ASSISTANT_TYPES:
                raise StaffError("助理类型参数不正确")
            query = query.filter(cls.model.assistant_type == assistant_type)
        total = query.count()
        items = (
            query.order_by(cls.model.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [cls.serialize(item) for item in items],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }

    @classmethod
    def get_item(cls, item_id: int):
        item = cls.model.query.filter(
            cls.model.id == item_id,
            cls.model.deleted_at.is_(None),
        ).first()
        if not item:
            raise StaffError(f"{cls.label}不存在", 404)
        return item

    @classmethod
    def create_item(cls, data: dict):
        payload = cls._validate_payload(data)
        cls._ensure_phone_available(payload["phone"])
        item = cls.model(**payload)
        db.session.add(item)
        db.session.commit()
        return item

    @classmethod
    def update_item(cls, item_id: int, data: dict):
        item = cls.get_item(item_id)
        payload = cls._validate_payload(data)
        cls._ensure_phone_available(payload["phone"], exclude_id=item.id)
        for key, value in payload.items():
            setattr(item, key, value)
        db.session.commit()
        return item

    @classmethod
    def delete_item(cls, item_id: int) -> None:
        item = cls.get_item(item_id)
        item.soft_delete()
        db.session.commit()

    @classmethod
    def _validate_payload(cls, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise StaffError(f"{cls.label}姓名不能为空")
        if len(name) > 50:
            raise StaffError(f"{cls.label}姓名不能超过 50 个字符")
        phone = (data.get("phone") or "").strip()
        if not phone:
            raise StaffError("手机号不能为空")
        if len(phone) > 20:
            raise StaffError("手机号不能超过 20 个字符")
        status = (data.get("status") or "active").strip()
        if status not in STAFF_STATUS:
            raise StaffError("状态参数不正确")
        remark = (data.get("remark") or "").strip()
        if len(remark) > 255:
            raise StaffError("备注不能超过 255 个字符")
        return {
            "avatar_object_key": data.get("avatar_object_key") or "",
            "name": name,
            "phone": phone,
            "status": status,
            "remark": remark,
        }

    @classmethod
    def _ensure_phone_available(cls, phone: str, exclude_id: int | None = None) -> None:
        query = cls.model.query.filter(
            cls.model.phone == phone,
            cls.model.deleted_at.is_(None),
        )
        if exclude_id is not None:
            query = query.filter(cls.model.id != exclude_id)
        if query.first():
            raise StaffError("手机号已存在")

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


class AssistantService(StaffService):
    model = Assistant
    label = "助理"

    @classmethod
    def _validate_payload(cls, data: dict) -> dict:
        payload = super()._validate_payload(data)
        assistant_type = (data.get("assistant_type") or "health_manager").strip()
        if assistant_type not in ASSISTANT_TYPES:
            raise StaffError("助理类型参数不正确")
        payload["assistant_type"] = assistant_type
        return payload


class CustomerServiceService(StaffService):
    model = CustomerService
    label = "客服"
