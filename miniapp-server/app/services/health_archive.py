from datetime import date, datetime

from app.extensions import db
from app.models import Assistant, ChatConversation, ChatConversationMember, Doctor, MiniappHealthRecord, MiniappUser
from app.services.chat import ChatService
from app.services.assistants import AssistantService
from app.services.doctors import DoctorService
from app.services.storage import StorageService
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
        is_member = bool(user.membership_expires_at and user.membership_expires_at > datetime.utcnow())
        return {
            "id": str(user.id),
            "name": user.real_name or user.nickname or "",
            "nickname": user.nickname or "",
            "avatar_object_key": user.avatar_object_key or "",
            "avatar_url": StorageService.sign_url(user.avatar_object_key),
            "phone": user.phone or "",
            "gender": user.gender or "unknown",
            "gender_label": HealthArchiveService._gender_label(user.gender),
            "birthday": user.birthday.isoformat() if user.birthday else "",
            "age": age,
            "membership_status": "active" if is_member else "none",
            "membership_label": "会员用户" if is_member else "普通用户",
            "membership_expires_at": beijing_iso(user.membership_expires_at),
            "created_at": beijing_iso(user.created_at),
            "last_login_at": beijing_iso(user.last_login_at),
        }

    @staticmethod
    def serialize_record(record: MiniappHealthRecord) -> dict:
        return {
            "id": str(record.id),
            "content": record.content or "",
            "image_object_keys": record.image_object_keys or [],
            "image_urls": StorageService.sign_urls(record.image_object_keys),
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
    def get_member_profile_by_conversation(
        viewer: MiniappUser,
        conversation_id: int,
        role: str,
        member_type: str,
        member_id: int,
    ) -> dict:
        viewer_type, viewer_id = ChatService._viewer_member(viewer, role)
        if member_type not in {"user", "doctor", "assistant"}:
            raise HealthArchiveError("成员类型不支持", 400)

        conversation = ChatConversation.query.filter(
            ChatConversation.id == conversation_id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if not conversation:
            raise HealthArchiveError("会话不存在", 404)

        viewer_member = HealthArchiveService._conversation_member(conversation.id, viewer_type, viewer_id)
        target_member = HealthArchiveService._conversation_member(conversation.id, member_type, member_id)
        if not viewer_member or not target_member:
            raise HealthArchiveError("无权查看该成员资料", 403)

        if member_type == "user":
            user = MiniappUser.query.filter(
                MiniappUser.id == member_id,
                MiniappUser.deleted_at.is_(None),
            ).first()
            if not user:
                raise HealthArchiveError("用户不存在", 404)
            return {
                "member_type": "user",
                "profile": HealthArchiveService.serialize_user(user),
                "archive": HealthArchiveService.serialize_archive(user),
            }

        if member_type == "doctor":
            doctor = Doctor.query.filter(
                Doctor.id == member_id,
                Doctor.deleted_at.is_(None),
            ).first()
            if not doctor or not doctor.department or doctor.department.deleted_at is not None:
                raise HealthArchiveError("医生不存在", 404)
            return {
                "member_type": "doctor",
                "profile": DoctorService.serialize(doctor, include_phone=True),
            }

        assistant = Assistant.query.filter(
            Assistant.id == member_id,
            Assistant.status == "active",
            Assistant.deleted_at.is_(None),
        ).first()
        if not assistant:
            raise HealthArchiveError("助理不存在", 404)
        return {
            "member_type": "assistant",
            "profile": AssistantService.serialize(assistant),
        }

    @staticmethod
    def _replace_records(user: MiniappUser, record_type: str, items: list[dict]) -> None:
        MiniappHealthRecord.query.filter(
            MiniappHealthRecord.user_id == user.id,
            MiniappHealthRecord.record_type == record_type,
        ).delete(synchronize_session=False)
        for index, item in enumerate(items):
            content = str(item.get("content") or "").strip()
            image_object_keys = item.get("image_object_keys") or item.get("image_urls") or []
            if not content and not image_object_keys:
                continue
            if not isinstance(image_object_keys, list):
                image_object_keys = []
            db.session.add(
                MiniappHealthRecord(
                    user_id=user.id,
                    record_type=record_type,
                    content=content,
                    image_object_keys=[str(url) for url in image_object_keys[:9]],
                    sort_order=index,
                )
            )

    @staticmethod
    def _conversation_member(conversation_id: int, member_type: str, member_id: int) -> ChatConversationMember | None:
        return ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation_id,
            ChatConversationMember.member_type == member_type,
            ChatConversationMember.member_id == member_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()

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
