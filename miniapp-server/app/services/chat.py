from datetime import datetime

from app.extensions import db
from app.models import (
    ChatConversation,
    ChatConversationMember,
    ChatMessage,
    ChatMessageAttachment,
    Doctor,
    MiniappUser,
)


class ChatError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


MESSAGE_TYPES = {"text", "image", "video"}


class ChatService:
    @staticmethod
    def get_or_create_single_conversation(user: MiniappUser, doctor_id) -> dict:
        try:
            doctor_id = int(doctor_id)
        except (TypeError, ValueError):
            raise ChatError("请选择医生") from None
        doctor = Doctor.query.filter(Doctor.id == doctor_id, Doctor.deleted_at.is_(None)).first()
        if not doctor or not doctor.department or doctor.department.deleted_at is not None:
            raise ChatError("医生不存在", 404)
        conversation = ChatConversation.query.filter(
            ChatConversation.conversation_type == "single",
            ChatConversation.owner_user_id == user.id,
            ChatConversation.doctor_id == doctor.id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if not conversation:
            conversation = ChatConversation(
                conversation_type="single",
                title=doctor.name,
                owner_user_id=user.id,
                doctor_id=doctor.id,
            )
            db.session.add(conversation)
            db.session.flush()
            db.session.add_all(
                [
                    ChatConversationMember(
                        conversation_id=conversation.id,
                        member_type="user",
                        member_id=user.id,
                    ),
                    ChatConversationMember(
                        conversation_id=conversation.id,
                        member_type="doctor",
                        member_id=doctor.id,
                    ),
                ]
            )
            db.session.commit()
        return ChatService.serialize_conversation(conversation, user)

    @staticmethod
    def list_conversations(user: MiniappUser) -> list[dict]:
        conversations = (
            ChatConversation.query.filter(
                ChatConversation.owner_user_id == user.id,
                ChatConversation.deleted_at.is_(None),
            )
            .order_by(ChatConversation.last_message_at.desc().nullslast(), ChatConversation.created_at.desc())
            .all()
        )
        return [ChatService.serialize_conversation(item, user) for item in conversations]

    @staticmethod
    def get_conversation(user: MiniappUser, conversation_id: int) -> ChatConversation:
        conversation = ChatConversation.query.filter(
            ChatConversation.id == conversation_id,
            ChatConversation.owner_user_id == user.id,
            ChatConversation.deleted_at.is_(None),
        ).first()
        if not conversation:
            raise ChatError("会话不存在", 404)
        return conversation

    @staticmethod
    def list_messages(user: MiniappUser, conversation_id: int, args) -> list[dict]:
        conversation = ChatService.get_conversation(user, conversation_id)
        limit = ChatService._positive_int(args.get("limit"), default=20, maximum=50)
        before_id = args.get("before_id")
        query = ChatMessage.query.filter(
            ChatMessage.conversation_id == conversation.id,
            ChatMessage.deleted_at.is_(None),
        )
        if before_id:
            try:
                query = query.filter(ChatMessage.id < int(before_id))
            except (TypeError, ValueError):
                raise ChatError("消息游标不正确") from None
        messages = query.order_by(ChatMessage.id.desc()).limit(limit).all()
        return [ChatService.serialize_message(item) for item in reversed(messages)]

    @staticmethod
    def send_message(user: MiniappUser, conversation_id: int, data: dict) -> dict:
        conversation = ChatService.get_conversation(user, conversation_id)
        message_type = data.get("message_type") or "text"
        if message_type not in MESSAGE_TYPES:
            raise ChatError("消息类型不支持")
        content = data.get("content") or ""
        attachments = data.get("attachments") or []
        if message_type == "text" and not content.strip():
            raise ChatError("消息内容不能为空")
        if message_type in {"image", "video"} and not attachments:
            raise ChatError("请上传附件")

        now = datetime.utcnow()
        message = ChatMessage(
            conversation_id=conversation.id,
            sender_type="user",
            sender_id=user.id,
            message_type=message_type,
            content=content,
            sent_at=now,
        )
        db.session.add(message)
        db.session.flush()

        for attachment in attachments:
            db.session.add(
                ChatMessageAttachment(
                    message_id=message.id,
                    file_type=attachment.get("file_type") or message_type,
                    file_url=attachment.get("file_url") or "",
                    thumbnail_url=attachment.get("thumbnail_url") or "",
                    file_name=attachment.get("file_name") or "",
                    mime_type=attachment.get("mime_type") or "",
                    file_size=attachment.get("file_size"),
                    duration_seconds=attachment.get("duration_seconds"),
                    width=attachment.get("width"),
                    height=attachment.get("height"),
                )
            )

        conversation.last_message_id = message.id
        conversation.last_message_type = message_type
        conversation.last_message_preview = ChatService._message_preview(message_type, content)
        conversation.last_message_at = now
        doctor_member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == "doctor",
            ChatConversationMember.member_id == conversation.doctor_id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if doctor_member:
            doctor_member.unread_count += 1
        db.session.commit()
        return ChatService.serialize_message(message)

    @staticmethod
    def mark_read(user: MiniappUser, conversation_id: int) -> None:
        conversation = ChatService.get_conversation(user, conversation_id)
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == "user",
            ChatConversationMember.member_id == user.id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        if member:
            member.unread_count = 0
            member.last_read_at = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def serialize_conversation(conversation: ChatConversation, user: MiniappUser) -> dict:
        doctor = conversation.doctor
        member = ChatConversationMember.query.filter(
            ChatConversationMember.conversation_id == conversation.id,
            ChatConversationMember.member_type == "user",
            ChatConversationMember.member_id == user.id,
            ChatConversationMember.deleted_at.is_(None),
        ).first()
        return {
            "id": str(conversation.id),
            "conversation_type": conversation.conversation_type,
            "doctor_id": str(doctor.id) if doctor else "",
            "doctor_name": doctor.name if doctor else conversation.title,
            "doctor_title": doctor.title if doctor else "",
            "department_name": doctor.department.name if doctor and doctor.department else "",
            "doctor_avatar": doctor.avatar_url if doctor else "",
            "last_message_preview": conversation.last_message_preview or "",
            "last_message_type": conversation.last_message_type or "",
            "last_message_at": conversation.last_message_at.isoformat()
            if conversation.last_message_at
            else None,
            "unread_count": member.unread_count if member else 0,
        }

    @staticmethod
    def serialize_message(message: ChatMessage) -> dict:
        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "sender_type": message.sender_type,
            "sender_id": str(message.sender_id),
            "role": "doctor" if message.sender_type == "doctor" else "user",
            "message_type": message.message_type,
            "content": message.content or "",
            "status": message.status,
            "sent_at": message.sent_at.isoformat() if message.sent_at else None,
            "attachments": [
                {
                    "id": str(item.id),
                    "file_type": item.file_type,
                    "file_url": item.file_url,
                    "thumbnail_url": item.thumbnail_url,
                    "file_name": item.file_name,
                    "mime_type": item.mime_type,
                    "file_size": item.file_size,
                    "duration_seconds": item.duration_seconds,
                    "width": item.width,
                    "height": item.height,
                }
                for item in message.attachments
            ],
        }

    @staticmethod
    def _message_preview(message_type: str, content: str) -> str:
        if message_type == "image":
            return "[图片]"
        if message_type == "video":
            return "[视频]"
        return content.strip()[:255]

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
