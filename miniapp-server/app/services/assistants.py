from app.models import Assistant, MiniappUser


class AssistantError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class AssistantService:
    @staticmethod
    def serialize(assistant: Assistant) -> dict:
        return {
            "id": str(assistant.id),
            "avatarUrl": assistant.avatar_url or "",
            "avatar": assistant.avatar_url or "",
            "name": assistant.name,
            "phone": assistant.phone,
            "title": "健康助理",
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
