from app.models import Assistant, MiniappUser
from app.extensions import db
from app.services.storage import StorageService


ASSISTANT_TYPE_LABELS = {
    "health_manager": "健康管家",
    "medical_assistant": "医疗助理",
}


class AssistantError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class AssistantService:
    @staticmethod
    def serialize(assistant: Assistant) -> dict:
        assistant_type = assistant.assistant_type or "health_manager"
        return {
            "id": str(assistant.id),
            "avatarObjectKey": assistant.avatar_object_key or "",
            "avatarUrl": StorageService.sign_url(assistant.avatar_object_key),
            "avatar": StorageService.sign_url(assistant.avatar_object_key),
            "name": assistant.name,
            "phone": assistant.phone,
            "title": ASSISTANT_TYPE_LABELS.get(assistant_type, "健康管家"),
            "assistant_type": assistant_type,
            "remark": assistant.remark or "",
            "status": assistant.status,
        }

    @staticmethod
    def list_assistants(args) -> list[dict]:
        keyword = (args.get("keyword") or "").strip()
        assistant_type = (args.get("assistant_type") or "").strip()
        query = Assistant.query.filter(
            Assistant.status == "active",
            Assistant.deleted_at.is_(None),
        )
        if assistant_type:
            if assistant_type not in ASSISTANT_TYPE_LABELS:
                raise AssistantError("助理类型参数不正确")
            query = query.filter(Assistant.assistant_type == assistant_type)
        if keyword:
            query = query.filter(
                db.or_(
                    Assistant.name.ilike(f"%{keyword}%"),
                    Assistant.phone.ilike(f"%{keyword}%"),
                    Assistant.remark.ilike(f"%{keyword}%"),
                )
            )
        items = query.order_by(Assistant.created_at.desc()).all()
        return [AssistantService.serialize(item) for item in items]

    @staticmethod
    def get_current_assistant(user: MiniappUser) -> dict:
        phone = (user.phone or "").strip()
        if not phone:
            raise AssistantError("当前登录用户未绑定手机号", 404)
        assistant = Assistant.query.filter(
            Assistant.phone == phone,
            Assistant.status == "active",
            Assistant.deleted_at.is_(None),
        ).first()
        if not assistant:
            raise AssistantError("当前手机号未匹配到助理信息", 404)
        return AssistantService.serialize(assistant)
