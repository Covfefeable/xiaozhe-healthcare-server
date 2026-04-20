from datetime import date, datetime

from app.extensions import db
from app.models import ChatConversation, ChatConversationMember, MiniappHealthRecord, MiniappUser
from app.services.chat import ChatService
from app.utils.time import beijing_iso


class HealthArchiveError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


RECORD_TYPES = {"medical_history", "medication"}


class HealthArchiveService:
    @staticmethod
    def serialize_user(user: MiniappUser) -> dict:
        age = HealthArchiveService._age(user.birthday)
        return {
            "id": str(user.id),
            "name": user.real_name or user.nickname or "",
            "nickname": user.nickname or "",
            "avatar_url": user.avatar_url or "",
            "phone": user.phone or "",
            "gender": user.gender or "unknown",
            "gender_label": HealthArchiveService._gender_label(user.gender),
            "birthday": user.birthday.isoformat() if user.birthday else "",
            "age": age,
            "created_at": beijing_iso(user.created_at),
            "last_login_at": beijing_iso(user.last_login_at),
        }

    @staticmethod
    def serialize_record(record: MiniappHealthRecord) -> dict:
        return {
            "id": str(record.id),
            "content": record.content or "",
            "image_urls": record.image_urls or [],
            "sort_order": record.sort_order,
            "created_at": beijing_iso(record.created_at),
            "updated_at": beijing_iso(record.updated_at),
        }

    @staticmethod
    def get_archive(user: MiniappUser) -> dict:
        return HealthArchiveService.serialize_archive(user)

    @staticmethod
    def serialize_archive(user: MiniappUser) -> dict:
        records = (
            MiniappHealthRecord.query.filter(
                MiniappHealthRecord.user_id == user.id,
                MiniappHealthRecord.deleted_at.is_(None),
            )
            .order_by(MiniappHealthRecord.record_type.asc(), MiniappHealthRecord.sort_order.asc(), MiniappHealthRecord.id.asc())
            .all()
        )
        grouped = {record_type: [] for record_type in RECORD_TYPES}
        for record in records:
            if record.record_type in grouped:
                grouped[record.record_type].append(HealthArchiveService.serialize_record(record))
        return {
            "basic_info": HealthArchiveService.serialize_user(user),
            "medical_histories": grouped["medical_history"],
            "medication_records": grouped["medication"],
        }

    @staticmethod
    def update_archive(user: MiniappUser, data: dict) -> dict:
        basic_info = data.get("basic_info") or {}
        if "name" in basic_info:
            user.real_name = str(basic_info.get("name") or "").strip()[:50]
        if "gender" in basic_info:
            gender = str(basic_info.get("gender") or "unknown").strip()
            user.gender = gender if gender in {"male", "female", "unknown"} else "unknown"
        if "birthday" in basic_info:
            user.birthday = HealthArchiveService._parse_date(basic_info.get("birthday"))

        HealthArchiveService._replace_records(user, "medical_history", data.get("medical_histories") or [])
        HealthArchiveService._replace_records(user, "medication", data.get("medication_records") or [])
        db.session.commit()
        return HealthArchiveService.serialize_archive(user)

    @staticmethod
    def get_archive_by_conversation(viewer: MiniappUser, conversation_id: int, role: str) -> dict:
        member_type, member_id = ChatService._viewer_member(viewer, role)
        conversation = ChatConversation.query.filter(
            ChatConversation.id == conversation_id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if not conversation:
            raise HealthArchiveError("会话不存在", 404)
        exists = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == member_type,
            ChatConversationMember.member_id == member_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if not exists or member_type not in {"doctor", "assistant"}:
            raise HealthArchiveError("无权查看该用户档案", 403)
        user = conversation.owner_user
        if not user or user.deleted_at is not None:
            raise HealthArchiveError("用户不存在", 404)
        return HealthArchiveService.serialize_archive(user)

    @staticmethod
    def _replace_records(user: MiniappUser, record_type: str, items: list[dict]) -> None:
        MiniappHealthRecord.query.filter(
            MiniappHealthRecord.user_id == user.id,
            MiniappHealthRecord.record_type == record_type,
        ).delete(synchronize_session=False)
        for index, item in enumerate(items):
            content = str(item.get("content") or "").strip()
            image_urls = item.get("image_urls") or []
            if not content and not image_urls:
                continue
            if not isinstance(image_urls, list):
                image_urls = []
            db.session.add(
                MiniappHealthRecord(
                    user_id=user.id,
                    record_type=record_type,
                    content=content,
                    image_urls=[str(url) for url in image_urls[:9]],
                    sort_order=index,
                )
            )

    @staticmethod
    def _parse_date(value) -> date | None:
        if not value:
            return None
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError:
            raise HealthArchiveError("出生日期格式不正确")

    @staticmethod
    def _age(birthday: date | None) -> int | None:
        if not birthday:
            return None
        today = date.today()
        return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    @staticmethod
    def _gender_label(gender: str | None) -> str:
        return {"male": "男", "female": "女"}.get(gender or "", "未填写")
