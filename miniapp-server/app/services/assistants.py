from app.models import Assistant, MiniappUser


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
            "avatarUrl": assistant.avatar_url or "",
            "avatar": assistant.avatar_url or "",
            "name": assistant.name,
            "phone": assistant.phone,
            "title": ASSISTANT_TYPE_LABELS.get(assistant_type, "健康管家"),
            "assistant_type": assistant_type,
            "remark": assistant.remark or "",
            "status": assistant.status,
        }

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
